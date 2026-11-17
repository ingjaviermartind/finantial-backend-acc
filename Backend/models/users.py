from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User

class Area(models.Model):
    key = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name 

class UserProfile(models.Model):

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
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name='profiles'
    )
    cargo = models.CharField(
        max_length=30,
        choices=Cargo.choices
    )
    def __str__(self):
        return f"{self.user.username} - {self.area} - {self.cargo}"