from django.db import models
from django.conf import settings
from uuid import uuid4
from .evaluations import EvaluationResult
from .catalog import Subsegment, Capacity, ProductCatalog
from .geography import Region, Municipality
from .users import Area


class FinancialVariable(models.Model):

    class Unit (models.TextChoices):
        USD = "USD"
        COP = "COP"
        COP_USD = "COP/USD"
        USD_MBPS_MES = "USD/Mbps/mes"
        USD_m = "USD/metro"
        COP_CALL = "COP/llamada"
        USD_POSTE_MES = "USD/poste/mes"
        USD_m_MES = "USD/metro/mes"
        PERCENT = "%"
        AD = "adimensional"
    def default_pricing_area():
        return Area.objects.get(key='pricing').pk
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name='financial_variables',
        default=default_pricing_area
    )
    key = models.SlugField(max_length=50)
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=6)
    unit = models.CharField(
        max_length=20,
        choices=Unit.choices
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['area', 'key'],
                name='unique_financial_variable_per_area'
            )
        ]
    def __str__(self):
        return f'{self.area.name} - {self.name}'



class ReferencePrice(models.Model):

    class PriceType(models.TextChoices):
        BASE = 'BASE', 'Tarifa Base'
        DISCOUNT = 'DISCOUNT', 'Tarifa con Descuento'
        SPECIAL = 'SPECIAL', 'Tarifa Especial'

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )
    subsegment = models.ForeignKey(
        Subsegment,
        on_delete=models.PROTECT,
        related_name='reference_prices',
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name='reference_prices'
    )
    capacity = models.ForeignKey(
        Capacity,
        on_delete=models.PROTECT,
        related_name='reference_prices'
    )
    price_type = models.CharField(
        max_length=20,
        choices=PriceType.choices,
        default=PriceType.BASE
    )
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'region',
                    'capacity',
                    'price_type'
                ],
                name='unique_reference_price'
            )
        ]
    def __str__(self):
        return (
            f'{self.region} | '
            f'{self.capacity} | '
            f'{self.get_price_type_display()}'
        )

class QuoteLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.PROTECT
    )
    subsegment = models.ForeignKey(
        Subsegment,
        on_delete=models.PROTECT,
        related_name='quote_logs'
    )
    product = models.ForeignKey(
        ProductCatalog,
        on_delete=models.PROTECT,
        related_name='quote_logs'
    )
    capacity = models.DecimalField(
        max_digits=15,
        decimal_places=6
    )

    contract_time = models.PositiveIntegerField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='quote_logs'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    suggested_price = models.ForeignKey(
        EvaluationResult,
        on_delete=models.PROTECT,
        related_name='suggested_price_quotes',
    )

    floor_price = models.ForeignKey(
        EvaluationResult,
        on_delete=models.CASCADE,
        related_name='floor_price_quotes',
    )

    class Meta:
        ordering = ['-created_at']