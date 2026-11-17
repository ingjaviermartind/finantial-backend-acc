from django.db import models


class DmPricingXSede(models.Model):
    nombre_de_pricing_por_sede = models.CharField(
        db_column='Nombre de Pricing por sede', 
        max_length=80, 
        blank=True, 
        null=True
    )   
    pricing_por_sede_on_off = models.CharField(
        db_column='Pricing Por Sede On/Off', 
        max_length=2
    )   
    pricing = models.CharField(
        db_column='Pricing', 
        max_length=80, 
        blank=True, 
        null=True
        )  
    sede = models.CharField(
        db_column='Sede', 
        max_length=80, 
        blank=True, 
        null=True
    )  
    arpu_mbps_cop_field = models.FloatField(
        db_column='ARPU/Mbps (COP$)', 
        blank=True, 
        null=True
    )  
    recurrente_mes = models.FloatField(
        db_column='Recurrente Mes', 
        blank=True, 
        null=True
    )
    # ultima_milla = models.FloatField(
    #     db_column='Ultima Milla', 
    #     blank=True, 
    #     null=True
    # )   
    # no_recurrente_mes = models.FloatField(
    #     db_column='No Recurrente Mes', 
    #     blank=True, 
    #     null=True
    # )   
    # kms_x_construir = models.FloatField(
    #     db_column='Kms X Construir', 
    #     blank=True, 
    #     null=True
    # )   
    # id_sf_pricing_x_sede = models.CharField(db_column='ID SF Pricing x Sede', max_length=80, blank=True, null=True)   
    porcentaje_de_descuento = models.DecimalField(
        db_column='Porcentaje De Descuento', 
        max_digits=18, 
        decimal_places=2, 
        blank=True, 
        null=True
    )   

    class Meta:
        managed = False
        db_table = '[SFDC].[DM_PRICING_X_SEDE]'