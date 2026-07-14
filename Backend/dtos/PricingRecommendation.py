from dataclasses import dataclass

from Backend.dtos.EvaluationResult import EvaluationResult


@dataclass
class PricingRecommendation:
    suggested: EvaluationResult
    predicted: EvaluationResult
    floor: EvaluationResult
    mean_price_mbps: float
    median_price_mbps: float
    market_std: float
    market_source: str
    market_sample: int
    