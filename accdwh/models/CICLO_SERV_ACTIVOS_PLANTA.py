from django.db import models


class CicloServActivosPlanta(models.Model):
    servicio = models.CharField(
        db_column='SERVICIO', 
        primary_key=True,
        max_length=80, 
    )
    ult_ciclo_fact = models.IntegerField(
        db_column='ULT_CICLO_FACT', 
        blank=True, 
        null=True
    )
    class Meta:
        managed = False
        db_table = '[DTM].[CICLO_SERV_ACTIVOS_PLANTA]'
        # db_table = 'CICLO_SERV_ACTIVOS_PLANTA'