from dataclasses import dataclass

@dataclass (slots = True)
class EvaluationResult:
    approved: bool
    capex : float
    opex_m : float
    price_monthly: float
    price_per_mbps: float
    vpn: float
    tir: float
    payback: int | None
    payback_percent : float
    margin: float
    cashflows: list[float]
    sensitivity: float | None = None