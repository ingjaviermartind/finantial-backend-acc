from django.db import models
from uuid import uuid4
from Backend.dtos import EvaluationResultDTO 
from dataclasses import asdict


class EvaluationResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    approved = models.BooleanField()
    price_monthly = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )
    price_per_mbps = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )
    vpn = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )
    tir = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )
    payback = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )
    margin = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )
    sensitivity = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )
    cashflows = models.JSONField()

    @classmethod
    def from_dto(cls, result: EvaluationResultDTO):
        return cls(
            approved=result.approved,
            price_monthly=result.price_monthly,
            price_per_mbps=result.price_per_mbps,
            vpn=result.vpn,
            tir=result.tir,
            payback=result.payback,
            margin=result.margin,
            cashflows=result.cashflows,
            sensitivity=result.sensitivity,
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

    project_snapshot = models.JSONField(default=dict)
    variables_snapshot = models.JSONField(default=dict)
    periods = models.JSONField(default=list)
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