from Backend.dtos import (
    Project, 
    FinancialVariables, 
    EvaluationResultDTO, 
    CashFlowPeriodDTO, 
    FinancialCashFlowDTO,
    ProjectEconomicsBuilder,
    ProjectEconomics
)
import numpy_financial as npf
from dataclasses import asdict, replace

class financial_engine:
    @staticmethod
    def calculate_capex(project : Project, variables : FinancialVariables) -> float:
        capex = project.capacity_mbps * project.contract_time * variables.trm * variables.web_capex
        return capex

    @staticmethod
    def calculate_opex(project : Project, variables : FinancialVariables) -> float:
        return (
            (project.capacity_mbps * variables.trm * variables.eth_output_mbps) 
            + variables.call_center
            + variables.oym

            + variables.poles
            + (variables.ducts * variables.trm)
            
            + variables.distribution
            + variables.collection
        )

    @staticmethod
    def evaluate_project(project : Project, variables : FinancialVariables) -> EvaluationResultDTO:
        # web_capex = financial_engine.calculate_capex(project, variables)
        # capex = web_capex + project.initial_capex
        # opex = financial_engine.calculate_opex(project, variables)
        # price_monthly = ((capex + (opex * project.contract_time)) / project.contract_time) * sensitivity * variables.margin_factor
        # price_monthly = round(price_monthly / 1000) * 1000
        economics : ProjectEconomics = ProjectEconomicsBuilder.build(
            project,
            variables
        )

        gmf = variables.gmf * economics.monthly_income
        fontic = variables.fontic * economics.monthly_income
        ica = variables.ica * economics.monthly_income
        cartera = variables.cartera * economics.monthly_income

        monthly_wacc = variables.monthly_wacc

        eth_output = (
            project.capacity_mbps
            * variables.trm
            * variables.eth_output_mbps
        )

        initial_gmf = project.initial_income * variables.gmf
        initial_fontic = project.initial_income * variables.fontic
        initial_ica = project.initial_income * variables.ica
        initial_taxes = initial_gmf + initial_fontic + initial_ica

        cashflows = []
        periods : CashFlowPeriodDTO = []
        vpn = 0
        income_vpn = 0
        payback = None
        ebitda_t = 0
        acc_fcl = 0

        for t in range (project.contract_time + 1):
            if t == 0:
                income = project.initial_income - initial_taxes if project.initial_income else 0
                current_capex = economics.capex
                current_gmf = initial_gmf
                current_fontic = initial_fontic
                current_ica = initial_ica
                current_cartera = 0

            else:
                income = economics.monthly_income
                current_capex = 0
                current_gmf = gmf
                current_fontic = fontic
                current_ica = ica
                current_cartera = cartera

            ebitda = income - economics.opex_monthly if t > 0 else 0 
            ebitda_dis = (
                ebitda
                - gmf
                - fontic
                - ica
                - cartera
            ) if t > 0 else 0 
            fcl = (income if t == 0 else ebitda_dis) - current_capex
            cashflows.append(fcl)
            acc_fcl = fcl if t == 0 else acc_fcl + fcl
            disc_factor = ((1 + monthly_wacc) ** t)
            disc_fcl = fcl / disc_factor 
            vpn += disc_fcl
            if payback is None and vpn > 0:
                if t == 0:
                    payback = 0
                else:
                    vpn_mes_anterior = vpn - disc_fcl
                    payback = (t - 1) + (abs(vpn_mes_anterior) / disc_fcl)
            income_vpn += (
                income / disc_factor
            )
            ebitda_t += ebitda_dis
            periods.append(
                CashFlowPeriodDTO(
                    period=t,
                    income=income,

                    eth_output=eth_output if t > 0 else 0,
                    oym=variables.oym if t > 0 else 0,
                    poles=variables.poles if t > 0 else 0,
                    ducts=(variables.ducts * variables.trm) if t > 0 else 0,
                    call_center=variables.call_center if t > 0 else 0,
                    distribution=variables.distribution if t > 0 else 0,
                    collection=variables.collection if t > 0 else 0,
                    opex=economics.opex_monthly if t > 0 else 0,

                    gmf=current_gmf,
                    fontic=current_fontic,
                    ica=current_ica,
                    cartera=current_cartera,

                    ebitda=ebitda,
                    ebitda_ajustado=ebitda_dis,

                    web_capex=economics.capex if t > 0 else 0,
                    initial_capex=current_capex,
                    fcl=fcl,
                    discount_factor=disc_factor,
                    discounted_fcl=disc_fcl,
                    accumulated_fcl=acc_fcl,
                    vpn=vpn,
                    income_vpn=income_vpn
                )
            )
        tir = npf.irr(cashflows)
        margin = vpn / income_vpn if income_vpn else 0
        approved = (
            vpn > variables.min_vpn
            and margin >= variables.min_margin
            and payback is not None
            and (payback / project.contract_time) <= variables.max_payback
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
            price_monthly=economics.monthly_income,
            price_per_mbps=economics.monthly_income / project.capacity_mbps,
            vpn=vpn,
            tir=tir,
            payback=payback,
            payback_percent = (payback / project.contract_time) if payback is not None else 0,
            margin=margin,
            cashflows=cashflows,
            sensitivity=project.sensitivity,
            financial_cashflow=financial_cashflow
        )

    
    @staticmethod
    def evaluate_price_per_mbps(project : Project, variables : FinancialVariables, value_mbps : float) -> EvaluationResultDTO:
        economics : ProjectEconomics = ProjectEconomicsBuilder.build(
            project,
            variables
        )
        target_monthly_income = value_mbps * project.capacity_mbps
        # capex = financial_engine.calculate_capex(project, variables) + project.initial_capex
        # opex = financial_engine.calculate_opex(project, variables)
        # price_monthly = capacity_mbps * project.capacity_mbps
        sensitivity = (
            target_monthly_income * economics.contract_time
            / ((economics.capex + economics.opex_monthly * economics.contract_time) * variables.margin_factor)
        )
        project_variant = replace(
            project,
            sensitivity=sensitivity
        )
        return financial_engine.evaluate_project(
            project_variant,
            variables
        )
