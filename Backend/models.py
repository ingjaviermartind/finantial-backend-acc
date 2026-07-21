from django.conf import settings
from django.db import models
from django.db.models import Q

from uuid import uuid4

class Price(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200)
    funnel = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='prices'
    )
    def __str__(self):
        return self.name

class PriceVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    price = models.ForeignKey(
        Price, 
        on_delete=models.CASCADE, 
        related_name='versions'
    )
    horizon = models.PositiveIntegerField(default=0)  # meses
    PAYMENT_TYPE = [
        ('one time', 'One time'),
        ('monthly', 'Monthly')
    ]
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    version_number = models.PositiveIntegerField()
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='price_versions'
    )
    class Meta:
        unique_together = ('price', 'horizon','version_number')
        constraints = [
            models.UniqueConstraint(
                fields=['price','horizon'],
                condition=Q(is_current=True),
                name='unique_current_version_per_price_horizon'
            )
        ]
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.price.name} v{self.version_number} {self.payment_type} ({self.horizon} month/s)"

class FinancialInputs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    version = models.OneToOneField(
        PriceVersion, 
        on_delete=models.CASCADE,
        related_name='inputs'
    )
    # horizon = models.PositiveIntegerField()  # meses
    inicial_income = models.FloatField(default=0.0)
    capex = models.FloatField()
    opex = models.FloatField()
    wacc = models.FloatField()
    factor = models.FloatField(default=1.0)
    sensitivity = models.FloatField(default=1.0)
    # PAYMENT_TYPE = [
    #     ('one time', 'One time'),
    #     ('monthly', 'Monthly')
    # ]
    # payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    # payment_duration = models.PositiveIntegerField(null=True, blank=True)
    def __str__(self):
        return f"Inputs {self.version}"

class CashFlow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    version = models.ForeignKey(
        PriceVersion, 
        on_delete=models.CASCADE,
        related_name='flows'
    )
    period = models.PositiveIntegerField()
    income = models.FloatField()
    opex = models.FloatField()
    ebitda = models.FloatField()
    capex = models.FloatField()
    fcl = models.FloatField()
    discount_factor = models.FloatField()
    fcl_discounted = models.FloatField()
    class Meta:
        unique_together = ('version', 'period')
        ordering = ['period']
    def __str__(self):
        return f'Flow {self.version} - period {self.period}'

class FinancialResults(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    version = models.OneToOneField(
        PriceVersion, 
        on_delete=models.CASCADE,
        related_name='results'
    )
    vpn = models.FloatField()
    income_vpn = models.FloatField(default=0)
    payback = models.FloatField()
    contribution_percent = models.FloatField()
    ebitda_total = models.FloatField()
    net_margin = models.FloatField(default=0)
    price = models.FloatField(default=0)
    def __str__(self):
        return f'Results {self.version}'

#
# Services Classes
#
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
    region = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.name

#
# EOF
#