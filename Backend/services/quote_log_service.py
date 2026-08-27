from Backend import models
from Backend.dtos.PricingRecommendation import PricingRecommendation
from django.db import transaction

class QuoteLogService:
    @staticmethod
    @transaction.atomic
    @staticmethod
    def create(
        result: PricingRecommendation,
        municipality,
        product,
        subsegment,
        project,
        user
    ):
        suggested = models.EvaluationResult.from_dto(
            result.suggested
        )
        suggested.save()

        floor = models.EvaluationResult.from_dto(
            result.floor
        )
        floor.save()

        return models.QuoteLog.objects.create(
            municipality=municipality,
            product=product,
            subsegment=subsegment,
            capacity=project.capacity_mbps,
            contract_time=project.contract_time,
            created_by=user,
            suggested_price=suggested,
            floor_price=floor
        )