from dataclasses import dataclass

@dataclass (slots = True)
class EvaluationResultDTO:
    approved: bool
    capex : float
    opex_m : float
    price_monthly: float
    price_per_mbps: float
    vpn: float
    tir: float
    payback: float | None
    payback_percent : float
    margin: float
    cashflows: list[float]
    sensitivity: float | None = None
    financial_cashflow : FinancialCashFlowDTO | None = None

@dataclass(slots=True)
class CashFlowPeriodDTO:
    period: int
    # Ingresos
    income: float
    # Desglose OPEX
    eth_output: float
    oym: float
    poles: float
    ducts: float
    call_center: float
    distribution: float
    collection: float
    opex: float
    # Cargos sobre ingresos
    gmf: float
    fontic: float
    ica: float
    cartera: float
    # Resultados
    ebitda: float
    ebitda_ajustado: float
    # Desglose CAPEX
    web_capex: float
    initial_capex: float
    # Flujo de caja
    fcl: float
    discount_factor: float
    discounted_fcl: float
    accumulated_fcl: float


@dataclass(slots=True)
class FinancialCashFlowDTO:
    project_snapshot: dict
    variables_snapshot: dict
    periods: list[CashFlowPeriodDTO]

@dataclass(slots=True)
class MonthlyDiscountDTO:
    period: int
    percentage: float