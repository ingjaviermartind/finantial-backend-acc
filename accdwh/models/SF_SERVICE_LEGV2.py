from django.db import models
from . import CicloServActivosPlanta

class SfServiceLegv2(models.Model):
    ser = models.CharField(
        db_column='SER', 
        max_length=80, 
        primary_key=True
    )  
    estado_ser = models.CharField(
        db_column='ESTADO_SER', 
        max_length=255, 
        blank=True, 
        null=True
    ) 
    fecha_cierre_servicio = models.DateTimeField(
        db_column='FECHA_CIERRE_SERVICIO', 
        blank=True, 
        null=True
    )  
    estado_instalaciones = models.CharField(
        db_column='ESTADO_INSTALACIONES',
        max_length=255, 
        blank=True,
        null=True
    )  
    razon_social = models.CharField(
        db_column='RAZON_SOCIAL', 
        max_length=255, 
        blank=True, 
        null=True
    ) 
    tipo_identificacion = models.CharField(
        db_column='TIPO_IDENTIFICACION', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    nro_identificacion = models.CharField(
        db_column='NRO_IDENTIFICACION', 
        max_length=50, 
        blank=True, 
        null=True
    )  
    digito_verificacion = models.CharField(
        db_column='DIGITO_VERIFICACION', 
        max_length=50, 
        blank=True, 
        null=True
    ) 
    @property
    def nit(self):
        if not self.nro_identificacion:
            return None
        if self.digito_verificacion:
            return f'{self.nro_identificacion}-{self.digito_verificacion}'
        return self.nro_identificacion
    @property
    def concat_nit(self):
        if not self.nro_identificacion:
            return None
        if self.digito_verificacion:
            return f'{self.nro_identificacion}{self.digito_verificacion}'
        return self.nro_identificacion
    plan = models.CharField(
        db_column='PLAN', 
        max_length=80, 
        blank=True, 
        null=True
    )   
    producto = models.CharField(
        db_column='PRODUCTO', 
        max_length=255,
        blank=True, 
        null=True
    )   
    tipo_producto = models.CharField(
        db_column='TIPO_PRODUCTO', 
        max_length=1300, 
        blank=True, 
        null=True
    )   
    tipo_tecnologia = models.CharField(
        db_column='TIPO_TECNOLOGIA', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    tarifa = models.DecimalField(
        db_column='TARIFA', 
        max_digits=18, 
        decimal_places=2, 
        blank=True, 
        null=True
    )   
    fecha_orden_servicio = models.DateTimeField(
        db_column='FECHA_ORDEN_SERVICIO', 
        blank=True, 
        null=True
    )   
    tipo_oferta = models.CharField(
        db_column='TIPO_OFERTA', 
        max_length=1300, 
        blank=True, 
        null=True
    )   
    fecha_inicio_permanencia = models.DateField(
        db_column='FECHA_INICIO_PERMANENCIA', 
        blank=True, 
        null=True
    )   
    fecha_fin_permanencia = models.DateField(
        db_column='FECHA_FIN_PERMANENCIA', 
        blank=True, 
        null=True
    )   
    meses_permanencia = models.DecimalField(
        db_column='MESES_PERMANENCIA', 
        max_digits=18, 
        decimal_places=2, 
        blank=True, 
        null=True
    )   
    acc_clp_clausulapermanencia_c = models.FloatField(
        db_column='ACC_CLP_ClausulaPermanencia__c', 
        blank=True, 
        null=True
    )   
    fechabaja = models.DateField(
        db_column='FechaBaja', 
        blank=True, 
        null=True
    )   
    ciclo = models.CharField(
        db_column='Ciclo', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    codigo_dane = models.CharField(
        db_column='Codigo DANE', 
        max_length=1300, 
        blank=True, 
        null=True
    )     
    # servicio_relacionado = models.CharField(db_column='Servicio Relacionado', max_length=80, blank=True, null=True)     
    # servicio_de_conectividad = models.CharField(db_column='Servicio de conectividad', max_length=80, blank=True, null=True)    
    anchodebanda = models.CharField(
        db_column='ANCHODEBANDA', 
        max_length=80, 
        blank=True, 
        null=True
    )   
    capacidadbps = models.DecimalField(
        db_column='CAPACIDADBPS', 
        max_digits=18, 
        decimal_places=2, 
        blank=True, 
        null=True
    )   
    # fechareiniciopermanencia = models.DateField(db_column='FechaReinicioPermanencia', blank=True, null=True)   
    tipodepunto = models.CharField(
        db_column='TipodePunto', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    acc_tipo_de_proyecto_c = models.CharField(
        db_column='ACC_Tipo_de_proyecto__c', 
        max_length=100, 
        blank=True, 
        null=True
    )   
    departamento = models.CharField(
        db_column='Departamento', 
        max_length=1300, 
        blank=True, 
        null=True
    )   
    municipio = models.CharField(
        db_column='Municipio', 
        max_length=1300, 
        blank=True, 
        null=True
    )   
    direccion_servicio = models.CharField(
        db_column='Direccion Servicio', 
        max_length=1300, 
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
    nvosubsegmento = models.CharField(
        db_column='NvoSubsegmento',
        max_length=255, 
        blank=True, 
        null=True
    )     
    linea_negocio = models.CharField(
        db_column='LINEA_NEGOCIO', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    familia_productos = models.CharField(
        db_column='FAMILIA_PRODUCTOS', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    correo_facturacion = models.CharField(
        db_column='CORREO_FACTURACION', 
        max_length=255, 
        blank=True, 
        null=True
    )      
    tipo_acceso_mpio = models.CharField(
        db_column='TIPO_ACCESO_MPIO', 
        max_length=1300, 
        blank=True, 
        null=True
    )   
    telefono = models.CharField(
        db_column='TELEFONO', 
        max_length=50, 
        blank=True, 
        null=True
    )   
    nombre_contacto_facturacion = models.CharField(
        db_column='NOMBRE_CONTACTO_FACTURACION', 
        max_length=100, 
        blank=True, 
        null=True
    )   
    apellido_contacto_facturacion = models.CharField(
        db_column='APELLIDO_CONTACTO_FACTURACION', 
        max_length=100, 
        blank=True, 
        null=True
    )   
    tipo_alta = models.CharField(
        db_column='TIPO_ALTA', 
        max_length=100, 
        blank=True, 
        null=True
    )   
    nombre_sucursal = models.CharField(
        db_column='NOMBRE_SUCURSAL', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    se_realiza_por_tercero = models.CharField(
        db_column='SE_REALIZA_POR_TERCERO',
        max_length=255, 
        blank=True, 
        null=True
    )   
    nombre_tercero_aliado = models.CharField(
        db_column='NOMBRE_TERCERO_ALIADO', 
        max_length=255, 
        blank=True, 
        null=True
    )   
    class Meta:
        managed = False
        db_table = '[DTM].[SF_SERVICE_LEGV2]'
        # db_table = 'SF_SERVICE_LEGV2'
