from django.db import models
from uuid import uuid4

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


class Department (models.Model):
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
    unprofitable = models.BooleanField(
        default=False
    )
    def __str__(self):
        return self.name
