from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User

class UserProfile(models.Model):

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