from Backend.dtos.Project import Project
from Backend.dtos.FinancialVariables import FinancialVariables
from Backend.dtos.EvaluationResult import EvaluationResult

import numpy_financial as npf

class financial_engine:
    @staticmethod
    def calculate_capex(project : Project, variables : FinancialVariables) -> float:
        return project.capacity_mbps * project.contract_time * variables.trm * variables.web_capex

    @staticmethod
    def calculate_opex(project : Project, variables : FinancialVariables) -> float:
        return (
            (project.capacity_mbps * variables.trm * variables.eth_output_mbps) 
            + variables.oym
            + variables.poles
            + variables.ducts
            + variables.call_center
            + variables.distribution
            + variables.collection
        )

    @staticmethod
    def evaluate_project(project : Project, variables : FinancialVariables, sensitivity) -> EvaluationResult:
        capex = financial_engine.calculate_capex(project, variables)
        opex = financial_engine.calculate_opex(project, variables)
        price_monthly = ((capex + (opex * project.contract_time)) / project.contract_time) * sensitivity * variables.margin_factor
        gmf = variables.gmf * price_monthly
        fontic = variables.fontic * price_monthly
        ica = variables.ica * price_monthly
        cartera = variables.cartera * price_monthly
        monthly_wacc = variables.monthly_wacc
        cashflows = []
        vpn = 0
        income_vpn = 0
        payback = None
        ebitda_t = 0
        acc_fcl = 0
        for t in range (project.contract_time + 1):
            if t == 0:
                income = project.initial_income if project.initial_income else 0
                current_capex = capex
            else:
                income = price_monthly
                current_capex = 0
            ebitda = (
                income
                - opex
                - gmf
                - fontic
                - ica
                - cartera
            ) if t > 0 else 0 
            fcl = ebitda - current_capex
            cashflows.append(fcl)
            acc_fcl = fcl if t == 0 else acc_fcl + ebitda
            disc_factor = ((1 + monthly_wacc) ** t)
            disc_fcl = fcl / disc_factor if t > 0 else 0
            if payback is None and acc_fcl > 0:
                payback = t
            vpn += disc_fcl
            income_vpn += (
                income / disc_factor
            )
            ebitda_t += ebitda
        tir = npf.irr(cashflows)
        margin = vpn / income_vpn if income_vpn else 0
        approved = (
            vpn > 0
            and margin >= 0.6
            and payback is not None
            and (payback / project.contract_time) <= 0.65
        )
        return EvaluationResult(
            approved=approved,
            price_monthly=price_monthly,
            price_per_mbps=price_monthly / project.capacity_mbps,
            vpn=vpn,
            tir=tir,
            payback=payback,
            margin=margin,
            cashflows=cashflows
        )
    
    @staticmethod
    def evaluate_price_per_mbps(project : Project, variables : FinancialVariables, capacity_mbps : float) -> EvaluationResult:
        capex = financial_engine.calculate_capex(project, variables)
        opex = financial_engine.calculate_opex(project, variables)
        price_monthly = capacity_mbps * project.capacity_mbps
        sensitivity = (
            price_monthly * project.contract_time
            / ((capex + opex * project.contract_time) * variables.margin_factor)
        )
        return financial_engine.evaluate_project(
            project,
            variables,
            sensitivity
        )
