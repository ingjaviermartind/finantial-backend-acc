
from django.db import models
from uuid import uuid4


class Subsegment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50,unique=True)
    is_active = models.BooleanField(default=True)
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

class ProductCatalog(models.Model):

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

    class ProductType(models.TextChoices):
        L2 = 'L2'
        L3 = 'L3'

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
#
# EOF
#