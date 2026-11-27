from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from uuid import uuid4
from Backend.dtos import EvaluationResultDTO 

from dataclasses import asdict


class EvaluationResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    approved = models.BooleanField()
    capex = models.DecimalField(max_digits=24, decimal_places=6)
    opex_m = models.DecimalField(max_digits=24, decimal_places=6)
    monthly_income = models.DecimalField(
        max_digits=24,
        decimal_places=6
    )
    vpn = models.DecimalField(
        max_digits=24,
        decimal_places=6
    )
    tir = models.DecimalField(
        max_digits=24,
        decimal_places=12,
        null=True,
        blank=True
    )
    payback = models.DecimalField(
        max_digits=24,
        decimal_places=8,
        null=True,
        blank=True
    )
    payback_percent = models.DecimalField(
        max_digits=24,
        decimal_places=12
    )
    margin = models.DecimalField(
        max_digits=24,
        decimal_places=12
    )

    @classmethod
    def from_dto(cls, result: EvaluationResultDTO):
        return cls(
            approved=result.approved,
            capex=result.capex,
            opex_m=result.opex_m,
            monthly_income=result.monthly_income,
            vpn=result.vpn,
            tir=result.tir,
            payback=result.payback,
            payback_percent=result.payback_percent,
            margin=result.margin
        )

class FinancialCashFlow(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )
    evaluation = models.OneToOneField(
        EvaluationResult,
        on_delete=models.PROTECT,
        related_name='financial_cashflow'
    )

    project_snapshot = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder
    )

    variables_snapshot = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder
    )

    periods = models.JSONField(
        default=list,
        encoder=DjangoJSONEncoder
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'financial_cashflows'
        ordering = ['created_at']
    def __str__(self):
        return f'Flujo de caja - {self.evaluation_id}'

    @classmethod
    def from_dto(cls, evaluation, dto):
        return cls(
            evaluation=evaluation,
            project_snapshot=dto.project_snapshot,
            variables_snapshot=dto.variables_snapshot,
            periods=[
                asdict(period)
                for period in dto.periods
            ]
        )