from dataclasses import dataclass

@dataclass (slots = True)
class EvaluationResult:
    approved: bool
    price_monthly: float
    price_per_mbps: float
    vpn: float
    tir: float
    payback: int | None
    margin: float
    cashflows: list[float]
    sensitivity: float | None = None