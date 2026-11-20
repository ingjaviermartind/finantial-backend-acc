from dataclasses import dataclass
from Backend.dtos import EvaluationResultDTO

@dataclass(frozen=True, slots=True)
class PricingRecommendation:
    suggested: EvaluationResultDTO
    predicted: EvaluationResultDTO
    floor: EvaluationResultDTO

    price_comparison: dict
    