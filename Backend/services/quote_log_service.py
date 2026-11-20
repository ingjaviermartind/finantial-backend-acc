
from Backend import models
from Backend.dtos import PricingRecommendation
from django.db import transaction


class QuoteLogService:

    @staticmethod
    def _save_evaluation(result_dto):
        # Guardar indicadores financieros
        evaluation = models.EvaluationResult.from_dto(result_dto)
        evaluation.save()
        # Validar que exista el flujo de caja
        if result_dto.financial_cashflow is None:
            raise ValueError("La evaluación no contiene información del flujo de caja.")
        # Construir y guardar el flujo de caja
        financial_cashflow = models.FinancialCashFlow.from_dto(
            evaluation=evaluation,
            dto=result_dto.financial_cashflow
        )
        financial_cashflow.save()
        return evaluation

    @staticmethod
    @transaction.atomic
    def create(
        result: PricingRecommendation,
        municipality,
        product,
        subsegment,
        project,
        user
    ):
        # Evaluación del precio sugerido + flujo de caja
        suggested = QuoteLogService._save_evaluation(result.suggested)
        # Evaluación del piso + flujo de caja
        floor = QuoteLogService._save_evaluation(result.floor)
        # Crear cotización
        quote = models.QuoteLog.objects.create(
            municipality=municipality,
            product=product,
            subsegment=subsegment,
            capacity=project.capacity_mbps,
            contract_time=project.contract_time,
            created_by=user,
            suggested_price=suggested,
            floor_price=floor
        )
        return quote
