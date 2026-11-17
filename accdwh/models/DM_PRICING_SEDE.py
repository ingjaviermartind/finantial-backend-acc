from django.db import models

class DmPricingSede(models.Model):
    consecutivo_de_sede = models.CharField(
        db_column='Consecutivo de Sede', 
        max_length=80, 
        blank=True, 
        null=True
    )   
    municipio = models.CharField(
        db_column='Municipio', 
        max_length=100, 
        blank=True, 
        null=True
    )  
    departamento = models.CharField(
        db_column='Departamento', 
        max_length=100, 
        blank=True, 
        null=True
    )  
    funnel = models.CharField(
        db_column='Funnel', 
        max_length=80, 
        blank=True, 
        null=True
    )  
    producto = models.CharField(
        db_column='Producto', 
        max_length=255, 
        blank=True, 
        null=True
    )  
    plan = models.CharField(
        db_column='Plan', 
        max_length=80, 
        blank=True, 
        null=True
    )  
    ancho_de_banda = models.CharField(
        db_column='Ancho de banda', 
        max_length=80, 
        blank=True, 
        null=True
    )   
    # field_cableoperador_field = models.CharField(db_column='┐Cableoperador?', max_length=2)    
    se_realizara_por_un_tercero = models.CharField(
        db_column='Se realizara por un tercero', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    ultimo_kilometro_uk = models.FloatField(
        db_column='Ultimo kilometro (UK)', 
        blank=True, 
        null=True
    )    
    tipo_de_tecnologia = models.CharField(
        db_column='Tipo de Tecnologia',
        max_length=255, 
        blank=True, 
        null=True
    )   
    distancia_fo_red_acc = models.FloatField(
        db_column='Distancia FO Red ACC', 
        blank=True, 
        null=True
    )   
    viabilidad_positiva = models.CharField(
        db_column='Viabilidad Positiva', 
        max_length=2
    )   
    distancia_total_viabilidad = models.FloatField(
        db_column='Distancia Total Viabilidad', 
        blank=True, 
        null=True
    )   
    total_por_un_punto_usd_viabilidad = models.FloatField(
        db_column='Total por un punto (USD) Viabilidad', 
        blank=True, 
        null=True
    )   
    total_opex_usd_viabilidad = models.FloatField(
        db_column='Total OpEx (USD) Viabilidad', 
        blank=True,
        null=True
    )   
    # observaciones_solicitud_preventa = models.CharField(
    #     db_column='Observaciones Solicitud Preventa', 
    #     max_length=3000, 
    #     blank=True,
    #     null=True
    # )   
    tipo_de_alta = models.CharField(
        db_column='Tipo de alta',
        max_length=500, 
        blank=True, 
        null=True
    )   
    latitud = models.FloatField(
        db_column='Latitud', 
        blank=True, 
        null=True
    )  
    longitud = models.FloatField(
        db_column='Longitud', 
        blank=True, 
        null=True
    )  
    direccion_sede = models.CharField(
        db_column='Direccion Sede', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    linea_negocio_sede = models.CharField(
        db_column='Linea_Negocio_Sede', 
        max_length=50, 
        blank=True, 
        null=True
    )  
    familia_producto_sede = models.CharField(
        db_column='Familia_Producto_Sede', 
        max_length=50, 
        blank=True, 
        null=True
    )  
    # tipo_producto_ser = models.CharField(db_column='Tipo_Producto_SER', max_length=20, blank=True, null=True)  
    region_tarifaria_sede = models.CharField(
        db_column='Region_Tarifaria_Sede', 
        max_length=50, 
        blank=True, 
        null=True
    )  
    dane_mpio = models.CharField(
        db_column='DANE_Mpio', 
        max_length=20, 
        blank=True, 
        null=True
    )  

    class Meta:
        managed = False
        db_table = '[SFDC].[DM_PRICING_SEDE]'