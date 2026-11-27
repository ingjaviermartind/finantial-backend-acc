from decimal import Decimal
import math
import numpy_financial as npf
from dataclasses import asdict, replace

from Backend.utils import ZERO, ONE, to_decimal

from Backend.dtos import (
    Project,
    MultiTelcoProject,
    FinancialVariables,
    EvaluationResultDTO,
    CashFlowPeriodDTO,
    FinancialCashFlowDTO,
    ProjectEconomicsBuilder,
    ProjectEconomics,
    GroupEvaluationDTO
)

class financial_engine:
    @staticmethod
    def evaluate_project(project : Project, variables : FinancialVariables, monthly_income: Decimal | None = None) -> EvaluationResultDTO:
        if project.contract_time <= 0:
            raise ValueError("El tiempo contractual debe ser mayor que cero.")
        economics : ProjectEconomics = ProjectEconomicsBuilder.build(project, variables)
        evaluated_income = economics.monthly_income if monthly_income is None else monthly_income
        if evaluated_income < ZERO:
            raise ValueError("El ingreso mensual no puede ser negativo.")
        
        gmf = variables.gmf * evaluated_income
        fontic = variables.fontic * evaluated_income
        ica = variables.ica * evaluated_income
        cartera = variables.cartera * evaluated_income

        initial_gmf = project.initial_income * variables.gmf
        initial_fontic = project.initial_income * variables.fontic
        initial_ica = project.initial_income * variables.ica

        initial_taxes = initial_gmf + initial_fontic + initial_ica

        monthly_wacc = variables.monthly_wacc

        periods : CashFlowPeriodDTO = []

        vpn = ZERO
        income_vpn = ZERO
        payback = None
        total_ebitda = ZERO
        accumulated_fcl = ZERO

        for t in range (project.contract_time + 1):
            if t == 0:
                income = project.initial_income - initial_taxes
                current_capex = economics.capex
                current_opex = ZERO

                capex_breakdown = economics.capex_breakdown.copy()
                opex_breakdown = {}

                current_gmf = initial_gmf
                current_fontic = initial_fontic
                current_ica = initial_ica
                current_cartera = ZERO

            else:
                income = evaluated_income
                current_capex = ZERO
                current_opex = economics.opex_monthly

                capex_breakdown = {}
                opex_breakdown = economics.opex_breakdown.copy()

                current_gmf = gmf
                current_fontic = fontic
                current_ica = ica
                current_cartera = cartera

            ebitda = income - current_opex if t > 0 else ZERO
            ebitda_adjusted = (
                ebitda
                - current_gmf
                - current_fontic
                - current_ica
                - current_cartera
            ) if t > 0 else ZERO

            fcl = (income if t == 0 else ebitda_adjusted) - current_capex

            accumulated_fcl += fcl
            discount_factor = (ONE + monthly_wacc) ** t
            discounted_fcl = fcl / discount_factor 

            vpn_km1 = vpn
            vpn += discounted_fcl

            if payback is None and vpn > ZERO:
                if t == 0:
                    payback = ZERO
                elif discounted_fcl > ZERO:
                    payback = (
                        Decimal(t - 1)
                        + abs(vpn_km1) / discounted_fcl
                    )
            income_vpn += income / discount_factor
            total_ebitda += ebitda_adjusted

            periods.append(
                CashFlowPeriodDTO(
                    period=t,
                    income=income,

                    capex_breakdown=capex_breakdown,
                    opex_breakdown=opex_breakdown,

                    capex=current_capex,
                    opex=current_opex,

                    gmf=current_gmf,
                    fontic=current_fontic,
                    ica=current_ica,
                    cartera=current_cartera,

                    ebitda=ebitda,
                    ebitda_ajustado=ebitda_adjusted,

                    fcl=fcl,
                    discount_factor=discount_factor,
                    discounted_fcl=discounted_fcl,
                    accumulated_fcl=accumulated_fcl,
                    vpn=vpn,
                    income_vpn=income_vpn
                )
            )
        tir_float = npf.irr([
            float(period.fcl)
            for period in periods
        ])
        tir = (
            to_decimal(tir_float)
            if tir_float is not None and math.isfinite(tir_float)
            else None
        )
        margin = vpn / income_vpn if income_vpn else ZERO
        payback_percent = (
            payback / Decimal(project.contract_time)
            if payback is not None
            else ZERO
        )
        approved = (
            vpn > variables.min_vpn
            and margin >= variables.min_margin
            and payback is not None
            and payback_percent <= variables.max_payback
        )
        financial_cashflow = FinancialCashFlowDTO(
            project_snapshot=asdict(project),
            variables_snapshot=asdict(variables),
            periods=periods
        )
        return EvaluationResultDTO(
            approved=approved,
            capex=economics.capex,
            opex_m=economics.opex_monthly,
            monthly_income=evaluated_income,
            vpn=vpn,
            tir=tir,
            payback=payback,
            payback_percent=payback_percent,
            margin=margin,
            financial_cashflow=financial_cashflow
        )

    @staticmethod
    def evaluate_group( project: MultiTelcoProject, variables: FinancialVariables) -> GroupEvaluationDTO:
        # 1. Evaluación consolidada
        consolidated = financial_engine.evaluate_project(
            project,
            variables
        )
        # 2. Evaluaciones individuales
        individual_results = [
            financial_engine.evaluate_project(
                product,
                variables
            )
            for product in project.products
        ]
        # 3. Construir resultado grupal
        return GroupEvaluationDTO(
            approved=consolidated.approved,
            capex=consolidated.capex,
            opex_m=consolidated.opex_m,
            monthly_income=consolidated.monthly_income,
            vpn=consolidated.vpn,
            tir=consolidated.tir,
            payback=consolidated.payback,
            payback_percent=consolidated.payback_percent,
            margin=consolidated.margin,
            financial_cashflow=consolidated.financial_cashflow,
            products=individual_results
        )

