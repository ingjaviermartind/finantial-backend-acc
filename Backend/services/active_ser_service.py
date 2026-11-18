
import pandas as pd
import re
import logging

from collections import defaultdict

from Backend import models
from Backend.dtos import MarketReference
from Backend.sql import ser_queries
from Backend.sql.database import engine

from sqlalchemy import text

from django.db.models import (
    Case,
    When,
    Value,
    CharField,
    F,
    Sum,
    IntegerField,
    DecimalField,
    ExpressionWrapper,
    OuterRef,
    Subquery,
    FloatField,
    Count,
    Sum,
    Q
)

from django.db.models.functions import (
    Cast,
    Concat,
    Replace,
    NullIf,
    Coalesce,
)

from accdwh.models import (
    SfServiceLegv2,
    CicloServActivosPlanta,
)

from statistics import median, mean, stdev
from decimal import Decimal


logger = logging.getLogger(__name__)


CAPACITY_GROUPS = [
    (2, 15, "2-15 Mbps"),
    (16, 74, "16-74 Mbps"),
    (75, 349, "75-349 Mbps"),
    (350, 1199, "350-1199 Mbps"),
    (1200, 2999, "1200-2999 Mbps"),
    (3000, 10000000, "3000+ Mbps"),
]


def get_capacity_group(capacity):
    if pd.isna(capacity):
        return None

    for min_cap, max_cap, label in CAPACITY_GROUPS:
        if min_cap <= capacity <= max_cap:
            return label

    return None


def get_clients_options():
    try:
        queryset = (
            SfServiceLegv2.objects.using('dwh')
            .exclude(
                estado_ser__in=[
                    'Cancelado',
                    'Error',
                    'En Proceso',
                    'Declinado'
                ]
            )
            .filter(estado_ser__isnull=False)
            .annotate(
                nit=Case(
                    When(
                        digito_verificacion__isnull=True,
                        then=Cast(
                            'nro_identificacion',
                            output_field=CharField()
                        )
                    ),
                    default=Concat(
                        F('nro_identificacion'),
                        Value('-'),
                        F('digito_verificacion')
                    ),
                    output_field=CharField()
                )
            )
            .values('nit', 'razon_social')
            .distinct()
            .order_by('nit', 'razon_social')
        )

        clients = defaultdict(set)

        for row in queryset:
            nit = row['nit']
            name = row['razon_social']

            if nit and name and name.strip():
                clients[nit].add(name.strip())

        data = [
            {
                'NIT': nit,
                'business_names': sorted(names)
            }
            for nit, names in sorted(clients.items())
        ]

        return {
            'success': True,
            'data': data
        }

    except Exception:
        logger.exception(
            "Error al consultar las opciones de clientes en DWH."
        )

        return {
            'success': False,
            'code': 'DATABASE_ERROR',
            'message': 'Error consultando la base de datos.'
        }

def get_services_options():
    try:
        services = (
            SfServiceLegv2.objects.using('dwh')
            .exclude(
                estado_ser__in=[
                    'Cancelado',
                    'Error',
                    'En Proceso',
                    'Declinado'
                ]
            )
            .filter(
                tipo_producto__in=['L2', 'L3']
            )
            .values(
                'ser',
                'razon_social',
                'producto',
                'nvosubsegmento',
                'capacidadbps',
                'anchodebanda',
                'departamento',
                'codigo_dane'
            )
            .order_by('ser')
        )

        data = list(services)

        for service in data:
            service['producto'] = format_product_name(
                service['producto']
            )

        return {
            'success': True,
            'data': data
        }

    except Exception:
        logger.exception(
            "Error al consultar las opciones de servicios en DWH."
        )

        return {
            'success': False,
            'code': 'DATABASE_ERROR',
            'message': 'Error consultando la base de datos.'
        }

def format_product_name(value: str | None) -> str | None:
    if not value:
        return None

    acronyms = ['IRU', 'IP', 'UK', 'ID', 'BA']
    formatted = value.strip().lower().title()

    for acronym in acronyms:
        formatted = re.sub(
            rf'\b{acronym.title()}\b',
            acronym,
            formatted,
            flags=re.IGNORECASE
        )

    return formatted

def _build_nit(nro_identificacion, digito_verificacion):
    """
    Construye el NIT conservando el comportamiento de la anotación ORM.
    Si no existe dígito de verificación, devuelve únicamente la identificación.
    """

    if nro_identificacion is None:
        if digito_verificacion is None:
            return None

        return f"-{digito_verificacion}"

    nit = str(nro_identificacion).strip()

    if digito_verificacion is not None:
        nit += f"-{digito_verificacion}"

    return nit

def _get_active_services_queryset():
    ciclo_subquery = (
        CicloServActivosPlanta.objects.using('dwh')
        .filter(servicio=OuterRef('ser'))
        .values('ult_ciclo_fact')[:1]
    )

    active_services = (
        SfServiceLegv2.objects.using('dwh')
        .exclude(
            estado_ser__in=[
                'Cancelado',
                'Error',
                'En Proceso',
                'Declinado'
            ]
        )
        .exclude(ser='SER-280627')
        .annotate(
            ser_number=Cast(
                Replace('ser', Value('SER-'), Value('')),
                output_field=IntegerField()
            )
        )
        .exclude(
            ser_number__range=(275470, 275731)
        )
        .annotate(
            nit=Case(
                When(
                    digito_verificacion__isnull=True,
                    then=Cast(
                        'nro_identificacion',
                        output_field=CharField()
                    )
                ),
                default=Concat(
                    'nro_identificacion',
                    Value('-'),
                    'digito_verificacion'
                ),
                output_field=CharField()
            )
        )
    )

    return (
        active_services
        .annotate(
            ult_ciclo_fact=Subquery(ciclo_subquery)
        )
        .annotate(
            ciclo_final=Coalesce(
                Cast('ult_ciclo_fact', output_field=CharField()),
                Cast('ciclo', output_field=CharField()),
                output_field=CharField()
            )
        )
        .filter(
            tipo_producto__in=['L2', 'L3', 'SATELITAL', 'SVA', 'SVAS'],
            tarifa__gt=1
        )
        .exclude(
            tipodepunto__in=[
                'Interconexion',
                'Interconexión - IRU',
                'Interconexion Backup'
            ]
        )
        .values(
            'ser',
            'ciclo_final',
            'departamento',
            'municipio',
            'codigo_dane',
            'nit',
            'razon_social',
            'nro_identificacion',
            'digito_verificacion',
            'anchodebanda',
            'capacidadbps',
            'tarifa',
            'fecha_fin_permanencia',
            'familia_productos',
            'producto',
            'plan',
            'tipo_tecnologia',
            'nvosubsegmento',
            'servicio_de_conectividad'
        )
    )

def _get_client_tariffs():
    """
    Calcula la tarifa total por cliente.

    Conserva las exclusiones utilizadas originalmente en active_services,
    pero realiza la agregación en SQL Server y construye el diccionario
    de NIT en Python.
    """

    services = (
        SfServiceLegv2.objects.using('dwh')
        .exclude(
            estado_ser__in=[
                'Cancelado',
                'Error',
                'En Proceso',
                'Declinado'
            ]
        )
        .exclude(ser='SER-280627')
        .annotate(
            ser_number=Cast(
                Replace('ser', Value('SER-'), Value('')),
                output_field=IntegerField()
            )
        )
        .exclude(
            ser_number__range=(275470, 275731)
        )
        .values(
            'nro_identificacion',
            'digito_verificacion'
        )
        .annotate(
            total=Sum('tarifa')
        )
    )

    client_tariffs = {}

    for row in services:
        nit = _build_nit(
            row['nro_identificacion'],
            row['digito_verificacion']
        )

        if nit is not None:
            client_tariffs[nit] = row['total']

    return client_tariffs

def _apply_service_filters(queryset, filters):
    if filters.departments:
        departments = list(
            models.Department.objects
            .filter(id__in=filters.departments)
            .values_list('name', flat=True)
        )

        queryset = queryset.filter(
            departamento__in=departments
        )

    if filters.municipalities:
        danes = list(
            models.Municipality.objects
            .filter(id__in=filters.municipalities)
            .values_list('dane', flat=True)
        )

        queryset = queryset.filter(
            codigo_dane__in=danes
        )

    if filters.product_families:
        queryset = queryset.filter(
            familia_productos__in=filters.product_families
        )

    if filters.products:
        queryset = queryset.filter(
            producto__in=filters.products
        )

    if filters.plans:
        queryset = queryset.filter(
            plan__in=filters.plans
        )

    if filters.capacity_min is not None:
        queryset = queryset.filter(
            capacidadbps__gte=filters.capacity_min
        )

    if filters.capacity_max is not None:
        queryset = queryset.filter(
            capacidadbps__lte=filters.capacity_max
        )

    if filters.clients:
        queryset = queryset.filter(
            nit__in=filters.clients
        )

    if filters.subsegments:
        subsegments = list(
            models.Subsegment.objects
            .filter(id__in=filters.subsegments)
            .values_list('name', flat=True)
        )

        queryset = queryset.filter(
            nvosubsegmento__in=subsegments
        )

    return queryset

def get_services(filters):
    stage = "Inicialización"
    try:
        logger.info("Iniciando consulta de servicios activos.")

        # 1. Construcción del queryset base
        stage = "Construcción del queryset base"

        queryset = _get_active_services_queryset()

        # 2. Aplicación de filtros
        stage = "Aplicación de filtros"

        queryset = _apply_service_filters(
            queryset,
            filters
        )

        # 2.1. Métricas de la población filtrada
        stage = "Cálculo de métricas"

        aggregates = queryset.aggregate(
            total_services=Count('ser'),
            unique_clients=Count('nit', distinct=True),
            total_mbps=Sum('capacidadbps'),
            total_mrc=Sum(
                'tarifa',
                filter=~Q(tipo_producto='SVAS')
            ),
            mrc_svas=Sum(
                'tarifa',
                filter=Q(tipo_producto='SVAS')
            )
        )

        metrics = {
            'total_services': aggregates['total_services'] or 0,
            'unique_clients': aggregates['unique_clients'] or 0,
            'total_mbps': aggregates['total_mbps'] or Decimal('0'),
            'total_mrc': aggregates['total_mrc'] or Decimal('0'),
            'mrc_svas': aggregates['mrc_svas'] or Decimal('0'),
        }

        # 3. Obtener códigos DANE
        stage = "Consulta de códigos DANE"

        danes = list(
            queryset.values_list(
                'codigo_dane',
                flat=True
            ).distinct()
        )

        # 4. Enriquecimiento de municipios
        stage = "Consulta de información municipal"

        municipality_data = {
            str(m['dane']).zfill(5): {
                'unprofitable': m['unprofitable'],
                'node': m['node'],
                'region': m['region__name'],
            }
            for m in models.Municipality.objects
                .filter(dane__in=danes)
                .values(
                    'dane',
                    'unprofitable',
                    'node',
                    'region__name'
                )
        }

        # 5. Consulta final de servicios
        stage = "Consulta final de servicios"

        final_queryset = (
            queryset
            .annotate(
                capacidad=F('anchodebanda'),
                vlr_mbps=ExpressionWrapper(
                    F('tarifa') / NullIf(
                        F('capacidadbps'),
                        Value(
                            0,
                            output_field=DecimalField(
                                max_digits=20,
                                decimal_places=4
                            )
                        )
                    ),
                    output_field=DecimalField(
                        max_digits=20,
                        decimal_places=6
                    )
                ),
                subsegmento=F('nvosubsegmento'),
            )
            .values(
                'ser',
                'ciclo_final',
                'departamento',
                'municipio',
                'codigo_dane',
                'nit',
                'razon_social',
                'capacidad',
                'capacidadbps',
                'tarifa',
                'vlr_mbps',
                'fecha_fin_permanencia',
                'familia_productos',
                'producto',
                'plan',
                'tipo_tecnologia',
                'subsegmento',
                'servicio_de_conectividad'
                
            )
            .order_by('-capacidadbps')
        )

        services = list(final_queryset)

        # 6. Obtener tarifas acumuladas por cliente
        stage = "Consulta de tarifas acumuladas por cliente"

        client_tariffs = _get_client_tariffs()

        # 7. Enriquecimiento de resultados
        stage = "Enriquecimiento de resultados"

        for service in services:
            nit = service['nit']

            service['tarifa_total_cliente'] = (
                client_tariffs.get(nit)
                if nit is not None
                else None
            )

            dane = str(
                service['codigo_dane'] or ''
            ).strip().zfill(5)

            municipality = municipality_data.get(dane, {})

            service['unprofitable'] = municipality.get(
                'unprofitable',
                False
            )

            service['node'] = municipality.get('node')
            service['region'] = municipality.get('region')

        logger.info(
            "Consulta finalizada. Servicios: %s | DANE: %s | "
            "Municipios: %s | Clientes con tarifa acumulada: %s",
            len(services),
            len(danes),
            len(municipality_data),
            len(client_tariffs)
        )

        return {
            'success': True,
            'metrics': metrics,
            'data': services
        }

    except Exception:
        logger.exception(
            "Error en get_services. Etapa: %s",
            stage
        )

        return {
            'success': False,
            'code': 'DATABASE_ERROR',
            'message': 'Error consultando la base de datos.'
        }

def _get_services_reference_queryset(
    min_cap,
    max_cap,
    subsegment,
    product
):
    return (
        SfServiceLegv2.objects.using('dwh')
        .exclude(
            estado_ser__in=[
                'Cancelado',
                'Error',
                'En Proceso',
                'Declinado'
            ]
        )
        .exclude(ser='SER-280627')
        .filter(
            tarifa__gt=10,
            capacidadbps__gt=0,
            capacidadbps__gte=min_cap,
            capacidadbps__lte=max_cap,
            nvosubsegmento=subsegment,
            producto=product
        )
        .annotate(
            vlr_mbps=ExpressionWrapper(
                Cast(F('tarifa'), FloatField()) /
                Cast(F('capacidadbps'), FloatField()),
                output_field=FloatField()
            )
        )
    )

def get_services_reference_by_municipality(
        municipality,
        min_cap,
        max_cap,
        subsegment,
        product
    ):
        MIN_SAMPLE = 5
        DEPT_SAMPLE = 5
        queryset = _get_services_reference_queryset(
            min_cap,
            max_cap,
            subsegment,
            product
        )
        # Referencia municipal
        municipality_qs = queryset.filter(
            codigo_dane=municipality.dane
        )
        if municipality_qs.count() >= MIN_SAMPLE:
            return _build_reference(
                municipality_qs,
                'municipality'
            )
        # Referencia departamental
        department_qs = queryset.filter(
            departamento=municipality.department.name
        )
        if department_qs.count() >= DEPT_SAMPLE:
            return _build_reference(
                department_qs,
                'department'
            )
        # Referencia nacional
        return _build_reference(
            queryset,
            'national'
        )


def _build_reference(queryset, source):
    values = list(
        queryset.values_list('vlr_mbps', flat=True)
    )
    sample_size = len(values)
    return MarketReference(
        source=source,
        sample_size=sample_size,
        median_price_mbps=float(median(values)) if values else None,
        mean_price_mbps=float(mean(values)) if values else None,
        std_price_mbps=float(stdev(values)) if sample_size > 1 else None
    )
