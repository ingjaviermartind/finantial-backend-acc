from django.db import models


class SfFunnelv2(models.Model):
    funnel = models.CharField(
        db_column='FUNNEL',
        max_length=80, 
        blank=True, 
        null=True
    )  
    servicio_funnel = models.CharField(
        db_column='SERVICIO_FUNNEL', 
        max_length=80, 
        blank=True, 
        null=True
    )  
    sede = models.CharField(
        db_column='SEDE', 
        max_length=80, 
        blank=True, 
        null=True
    )  
    estado_funnel = models.CharField(
        db_column='ESTADO_FUNNEL', 
        max_length=255, 
        blank=True, 
        null=True
    )  
    # fecha_cliente_no_acepta_funnel = models.DateField(db_column='FECHA_CLIENTE_NO_ACEPTA_FUNNEL', blank=True, null=True)  
    modelo_oferta = models.CharField(
        db_column='MODELO_OFERTA', 
        max_length=3000, 
        blank=True, 
        null=True
    )  
    nombre_comercial_funnel = models.CharField(
        db_column='NOMBRE_COMERCIAL_FUNNEL', 
        max_length=255, 
        blank=True, 
        null=True
    )  
    # tipo_identificacion_funnel = models.CharField(db_column='TIPO_IDENTIFICACION_FUNNEL', max_length=255, blank=True, null=True)  
    nro_identificacion_cliente_funnel = models.CharField(
        db_column='NRO_IDENTIFICACION_CLIENTE_FUNNEL', 
        max_length=27, 
        blank=True, 
        null=True
    )  
    digito_verificacion_funnel = models.FloatField(
        db_column='DIGITO_VERIFICACION_FUNNEL',
        blank=True, 
        null=True
    )  
    # observaciones_funnel = models.CharField(db_column='OBSERVACIONES_FUNNEL', max_length=255, blank=True, null=True)  
    periodo_funnel = models.CharField(
        db_column='PERIODO_FUNNEL', 
        max_length=3000, 
        blank=True, 
        null=True
    )  
    target_mrc_grupal_funnel = models.FloatField(
        db_column='TARGET_MRC_GRUPAL_FUNNEL', 
        blank=True, 
        null=True
    )  
    # cantidad_sedes_funnel = models.FloatField(db_column='CANTIDAD_SEDES_FUNNEL', blank=True, null=True)  
    # capacidad_maxima = models.FloatField(db_column='CAPACIDAD_MAXIMA', blank=True, null=True)  
    # total_sedes_con_capacidad = models.FloatField(db_column='TOTAL_SEDES_CON_CAPACIDAD', blank=True, null=True)  
    # nombre_canal = models.CharField(db_column='NOMBRE_CANAL', max_length=255, blank=True, null=True)  
    fechacreacion = models.DateTimeField(
        db_column='FechaCreacion', 
        blank=True, 
        null=True
    )  
    tipooferta = models.CharField(
        db_column='TipoOferta', 
        max_length=255, 
        blank=True, 
        null=True
    )  
    # ultima_fecha_modificacion_funnel = models.DateTimeField(db_column='ULTIMA_FECHA_MODIFICACION_FUNNEL', blank=True, null=True)  
    # solicitud_preventa = models.CharField(db_column='Solicitud_Preventa', max_length=80, blank=True, null=True)  
    # complejidad = models.CharField(db_column='Complejidad', max_length=255, blank=True, null=True)  
    clave_vendedor_funnel = models.CharField(
        db_column='CLAVE_VENDEDOR_FUNNEL', 
        max_length=255, 
        blank=True, 
        null=True
    )  

    class Meta:
        managed = False
        db_table = '[DTM].[SF_FUNNELV2]'
        # db_table = 'SF_FUNNELV2'
