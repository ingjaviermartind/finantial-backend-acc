from django.conf import settings
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User

from Backend.dtos.EvaluationResult import EvaluationResult

from uuid import uuid4

# class Price(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
#     name = models.CharField(max_length=200)
#     funnel = models.CharField(max_length=50)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE, 
#         related_name='prices'
#     )
#     def __str__(self):
#         return self.name

# class PriceVersion(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
#     price = models.ForeignKey(
#         Price, 
#         on_delete=models.CASCADE, 
#         related_name='versions'
#     )
#     horizon = models.PositiveIntegerField(default=0)  # meses
#     PAYMENT_TYPE = [
#         ('one time', 'One time'),
#         ('monthly', 'Monthly')
#     ]
#     payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
#     version_number = models.PositiveIntegerField()
#     is_current = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE, 
#         related_name='price_versions'
#     )
#     class Meta:
#         unique_together = ('price', 'horizon','version_number')
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['price','horizon'],
#                 condition=Q(is_current=True),
#                 name='unique_current_version_per_price_horizon'
#             )
#         ]
#         ordering = ['-created_at']
#     def __str__(self):
#         return f"{self.price.name} v{self.version_number} {self.payment_type} ({self.horizon} month/s)"

# class FinancialInputs(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
#     version = models.OneToOneField(
#         PriceVersion, 
#         on_delete=models.CASCADE,
#         related_name='inputs'
#     )
#     # horizon = models.PositiveIntegerField()  # meses
#     inicial_income = models.FloatField(default=0.0)
#     capex = models.FloatField()
#     opex = models.FloatField()
#     wacc = models.FloatField()
#     factor = models.FloatField(default=1.0)
#     sensitivity = models.FloatField(default=1.0)
#     # PAYMENT_TYPE = [
#     #     ('one time', 'One time'),
#     #     ('monthly', 'Monthly')
#     # ]
#     # payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
#     # payment_duration = models.PositiveIntegerField(null=True, blank=True)
#     def __str__(self):
#         return f"Inputs {self.version}"

# class CashFlow(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
#     version = models.ForeignKey(
#         PriceVersion, 
#         on_delete=models.CASCADE,
#         related_name='flows'
#     )
#     period = models.PositiveIntegerField()
#     income = models.FloatField()
#     opex = models.FloatField()
#     ebitda = models.FloatField()
#     capex = models.FloatField()
#     fcl = models.FloatField()
#     discount_factor = models.FloatField()
#     fcl_discounted = models.FloatField()
#     class Meta:
#         unique_together = ('version', 'period')
#         ordering = ['period']
#     def __str__(self):
#         return f'Flow {self.version} - period {self.period}'

# class FinancialResults(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
#     version = models.OneToOneField(
#         PriceVersion, 
#         on_delete=models.CASCADE,
#         related_name='results'
#     )
#     vpn = models.FloatField()
#     income_vpn = models.FloatField(default=0)
#     payback = models.FloatField()
#     contribution_percent = models.FloatField()
#     ebitda_total = models.FloatField()
#     net_margin = models.FloatField(default=0)
#     price = models.FloatField(default=0)
#     def __str__(self):
#         return f'Results {self.version}'

#
# Services Classes
#
class Subsegment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50,unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Unit (models.TextChoices):
    USD = "USD",
    COP = "COP"
    COP_USD = "COP/USD"
    USD_MBPS_MES = "USD/Mbps/mes"
    USD_m = "USD/metro"
    COP_CALL = "COP/llamada"
    USD_POSTE_MES = "USD/poste/mes"
    USD_m_MES = "USD/metro/mes"
    PERCENT = "%"
    AD = "adimensional"

class FinancialVariable(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=6)
    unit = models.CharField(
        max_length=20,
        choices=Unit.choices
    )
    updated_at = models.DateTimeField(auto_now=True)

class Zone (models.TextChoices):
    NORTH = "NORTH", "NORTE"
    COFFEE_AXIS = "COFFEE AXIS", "EJE CAFETERO"
    CENTER = "CENTER", "CENTRO"
    SOUTH = "SOUTH", "SUR"
    EAST = "EAST", "ORIENTE"
    WEST = "WEST", "OCCIDENTE"
    BOYACA = "BOYACA"
    NORTE_SANTANDER = "NORTE DE SANTANDER"
    NONE = "NONE", "NINGUNO"

class Region(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=100,
        unique=True
    )
    def __str__(self):
        return self.name

class Capacity(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )
    mbps=models.PositiveIntegerField(
        unique=True
    )
    def __str__(self):
        return f'{self.mbps} Mbps'

class PriceType(models.TextChoices):
    BASE = 'BASE', 'Tarifa Base'
    DISCOUNT = 'DISCOUNT', 'Tarifa con Descuento'
    SPECIAL = 'SPECIAL', 'Tarifa Especial'

class ReferencePrice(models.Model):
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

class Department (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    zone = models.CharField(
        max_length=50,
        choices=Zone.choices
    )
    avg_rate_pf = models.FloatField()
    def __str__(self):
        return self.name
    
class Municipality (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='municipalities'
    )
    name = models.CharField(max_length=100)
    dane = models.PositiveIntegerField()
    latitude = models.FloatField(
        null=True,
        blank=True
    )
    longitude = models.FloatField(
        null=True,
        blank=True
    )
    node = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    region = models.ForeignKey(
        Region,
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )
    def __str__(self):
        return self.name



class Area(models.TextChoices):
    PRICING = 'pricing'
    RETENCION = 'retencion'
    VENTAS = 'ventas'
    PREVENTA = 'preventa'

class Cargo(models.TextChoices):
    ANALISTA = 'analista'
    PROFESIONAL = 'profesional'
    INGENIERO = 'ingeniero'
    LIDER = 'lider'
    GERENTE = 'gerente'
    DIRECTOR = 'director'

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    area = models.CharField(
        max_length=30,
        choices=Area.choices
    )
    cargo = models.CharField(
        max_length=30,
        choices=Cargo.choices
    )
    def __str__(self):
        return f"{self.user.username} - {self.area} - {self.cargo}"





class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    verification_number = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    identification_number = models.PositiveIntegerField(default = 0)
    name = models.CharField(max_length=50)
    subsegment = models.ForeignKey(
        Subsegment,
        on_delete=models.PROTECT,
        related_name='clients',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.name

class ProductType(models.TextChoices):
    L2 = 'L2'
    L3 = 'L3'

class Product(models.TextChoices):
    CANAL_NACIONAL = 'Canal Nacional'
    CANAL_NACIONAL_SIN_UK = 'Canal Nacional Ethernet sin UK'
    BA_CORPORATIVA = 'BA Corporativa'
    ID_CORPORATIVO = 'ID Corporativo'
    INTERNET_PLUS = 'Internet +'
    INTERNET_DEDICADO_EMP = 'Internet Dedicado Empresarial'
    INTERNET_DEDICADO_SIN_UK = 'Internet Dedicado sin UK'
    INTERNET_SIMETRICO_EMP = 'Internet Simetrico Empresarial'
    RED_IP = 'Red IP'
    IRU_CAPACIDAD = 'IRU de Capacidad'


class ProductCatalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product_type = models.CharField(
        max_length=10,
        choices=ProductType.choices
    )
    product = models.CharField(
        max_length=50,
        choices=Product.choices
    )
    is_active = models.BooleanField(default=True)
    class Meta:
        unique_together = ("product_type", "product")
    def __str__(self):
        return f"{self.product_type} - {self.product}"

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
    capacity = models.FloatField()
    contract_time = models.FloatField()

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
#
# EOF
#