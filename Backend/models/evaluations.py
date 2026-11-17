from __future__ import annotations

from django.db import models
from uuid import uuid4

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
    def from_dto(cls, result: EvaluationResult):
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