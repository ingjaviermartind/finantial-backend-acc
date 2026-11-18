from dataclasses import dataclass
from Backend.dtos import EvaluationResult

@dataclass(frozen=True, slots=True)
class PricingRecommendation:
    suggested: EvaluationResult
    predicted: EvaluationResult
    floor: EvaluationResult

    price_comparison: dict
    