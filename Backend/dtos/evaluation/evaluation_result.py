from dataclasses import dataclass
from typing import ClassVar
from decimal import Decimal

@dataclass(slots=True)
class CashFlowPeriodDTO:
    period: int
    income: Decimal
    # Desglose OPEX
    capex_breakdown: dict[str, Decimal]
    opex_breakdown: dict[str, Decimal]

    capex : Decimal
    opex: Decimal

    gmf: Decimal
    fontic: Decimal
    ica: Decimal
    cartera: Decimal

    ebitda: Decimal
    ebitda_ajustado: Decimal

    # Flujo de caja
    fcl: Decimal
    discount_factor: Decimal
    discounted_fcl: Decimal
    accumulated_fcl: Decimal
    vpn : Decimal
    income_vpn : Decimal

@dataclass(slots=True)
class FinancialCashFlowDTO:
    project_snapshot: dict
    variables_snapshot: dict
    periods: list[CashFlowPeriodDTO]

@dataclass (slots = True)
class EvaluationResultDTO:
    approved: bool
    capex : Decimal
    opex_m : Decimal
    monthly_income: Decimal
    vpn: Decimal
    tir: Decimal | None
    payback: Decimal | None
    payback_percent : Decimal
    margin: Decimal
    financial_cashflow : FinancialCashFlowDTO | None = None

@dataclass(slots=True)
class IndividualEvaluationDTO(EvaluationResultDTO):
    evaluation_type: ClassVar[str] = "individual"


@dataclass(slots=True)
class GroupEvaluationDTO(EvaluationResultDTO):
    evaluation_type: ClassVar[str] = "group"
    products: list[IndividualEvaluationDTO] | None = None

@dataclass(slots=True)
class MonthlyDiscountDTO:
    period: int
    percentage: Decimal