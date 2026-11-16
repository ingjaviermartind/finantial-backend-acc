from django.db import models
from uuid import uuid4
from .catalog import Subsegment

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