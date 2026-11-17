import pandas as pd
from Backend import models

from Backend.dtos import MarketReference

from Backend.sql import ser_queries
from Backend.sql.database import engine
from sqlalchemy import text

from collections import defaultdict
from django.db.models import (Case, When, Value, CharField, F, OuterRef, Subquery, Sum, IntegerField, DecimalField, ExpressionWrapper)
from django.db.models.functions import Cast, Concat, Replace, NullIf, Coalesce
from accdwh.models import SfServiceLegv2, CicloServActivosPlanta
import re

import logging
logger = logging.getLogger(__name__)

CAPACITY_GROUPS = [
    (2, 15, "2-15 Mbps"),
    (16, 74, "16-74 Mbps"),
    (75, 349, "75-349 Mbps"),
    (350, 1199, "350-1199 Mbps"),
    (1200, 2999, "1200-2999 Mbps"),
    (3000, 10000000, "3000+ Mbps"),
]

@staticmethod
def get_capacity_group(capacity):
    if pd.isna(capacity):
        return None

    for min_cap, max_cap, label in CAPACITY_GROUPS:
        if min_cap <= capacity <= max_cap:
            return label

    return None




@staticmethod
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

@staticmethod
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
        logger.exception("Error al consultar las opciones de servicios en DWH.")
        return {
            'success': False,
            'code': 'DATABASE_ERROR',
            'message': 'Error consultando la base de datos.'
        }

@staticmethod
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

@staticmethod
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
    client_tariff = (
        active_services
        .filter(nit=OuterRef('nit'))
        .values('nit')
        .annotate(total=Sum('tarifa'))
        .values('total')[:1]
    )
    return (
        active_services
        .annotate(
            ult_ciclo_fact=Subquery(ciclo_subquery),
            ciclo_final=Coalesce(
                Cast('ult_ciclo_fact', output_field=CharField()),
                Cast('ciclo', output_field=CharField()),
                output_field=CharField()
            ),
            tarifa_total_cliente=Subquery(client_tariff)
        )
        .filter(
            tipo_producto__in=['L2', 'L3', 'SATELITAL'],
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
            'tarifa_total_cliente',
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

@staticmethod
def _apply_service_filters(queryset, filters):
    if filters.departments:
        departments = list(
            models.Department.objects
            .filter(id__in=filters.departments)
            .values_list('name', flat=True)
        )
        queryset = queryset.filter(departamento__in=departments)

    if filters.municipalities:
        danes = list(
            models.Municipality.objects
            .filter(id__in=filters.municipalities)
            .values_list('dane', flat=True)
        )
        queryset = queryset.filter(codigo_dane__in=danes)

    if filters.product_families:
        queryset = queryset.filter(
            familia_productos__in=filters.product_families
        )

    if filters.products:
        queryset = queryset.filter(producto__in=filters.products)

    if filters.plans:
        queryset = queryset.filter(plan__in=filters.plans)

    if filters.capacity_min is not None:
        queryset = queryset.filter(
            capacidadbps__gte=filters.capacity_min
        )

    if filters.capacity_max is not None:
        queryset = queryset.filter(
            capacidadbps__lte=filters.capacity_max
        )

    if filters.clients:
        queryset = queryset.filter(nit__in=filters.clients)

    if filters.subsegments:
        subsegments = list(
            models.Subsegment.objects
            .filter(id__in=filters.subsegments)
            .values_list('name', flat=True)
        )
        queryset = queryset.filter(nvosubsegmento__in=subsegments)
    return queryset

@staticmethod
def get_services(filters):
    try:
        queryset = _get_active_services_queryset()
        queryset = _apply_service_filters(
            queryset,
            filters
        )
        # Obtener los DANE presentes en los servicios filtrados
        danes = list(
            queryset.values_list(
                'codigo_dane',
                flat=True
            ).distinct()
        )
        # Enriquecer únicamente los municipios correspondientes
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
        services = list(
            queryset
            .annotate(
                capacidad=F('anchodebanda'),
                vlr_mbps=ExpressionWrapper(
                    F('tarifa') / NullIf(
                        F('capacidadbps'),
                        Value(0, output_field=DecimalField(
                            max_digits=20,
                            decimal_places=4
                        ))
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
                'departamento',
                'municipio',
                'codigo_dane',
                'nit',
                'razon_social',
                'tarifa_total_cliente',
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
                'ciclo_final'
            )
            .order_by('-capacidadbps')
        )

        for service in services:
            dane = str(service['codigo_dane'] or '').strip().zfill(5)
            municipality = municipality_data.get(dane, {})
            service['unprofitable'] = municipality.get('unprofitable', False)
            service['node'] = municipality.get('node')
            service['region'] = municipality.get('region')

        return {
            'success': True,
            'data': services
        }

    except Exception:
        logger.exception("Error al consultar servicios activos con los filtros aplicados.")
        return {
            'success': False,
            'code': 'DATABASE_ERROR',
            'message': 'Error consultando la base de datos.'
        }
    


@staticmethod
def get_services_reference_by_municipality(municipality, min_cap, max_cap):
    MIN_SAMPLE = 5
    DEPT_SAMPLE = 5
    with engine.connect() as conn:
        df_services_reference = pd.read_sql(
            text(ser_queries.QUERY_SERVICES_REFERENCE_MUN),
            conn,
            params={
                "dane": municipality.dane,
                "min_cap": min_cap,
                "max_cap": max_cap
            }
        )
        if len(df_services_reference) >= MIN_SAMPLE:
            return _build_reference(
                df_services_reference,
                'municipality'
            )
        df_services_reference = pd.read_sql(
            text(ser_queries.QUERY_SERVICES_REFERENCE_DEPT),
            conn,
            params={
                "department": municipality.department.name,
                "min_cap": min_cap,
                "max_cap": max_cap
            }
        )
        if len(df_services_reference) >= DEPT_SAMPLE:
            return _build_reference(
                df_services_reference,
                'department'
            )
        df_services_reference = pd.read_sql(
            text(ser_queries.QUERY_SERVICES_REFERENCE_NATIONAL),
            conn,
            params={
                "min_cap": min_cap,
                "max_cap": max_cap
            }
        )

        return _build_reference(
            df_services_reference,
            'national'
        )
    # conn = pyodbc.connect(
    #     r"DRIVER={ODBC Driver 17 for SQL Server};"
    #     r"SERVER=10.142.16.246\accdwh;"
    #     r"DATABASE=Azteca_Staging;"
    #     r"Trusted_Connection=yes;"
    # )
    # try:
    #     df_services_reference = pd.read_sql(
    #         ser_queries.QUERY_SERVICES_REFERENCE_MUN, 
    #         conn,
    #         params=[municipality.dane, min_cap, max_cap]
    #     )
    #     if len(df_services_reference) >= MIN_SAMPLE:
    #         return _build_reference(df_services_reference,'municipality')
    #     df_services_reference = pd.read_sql(
    #         ser_queries.QUERY_SERVICES_REFERENCE_DEPT, 
    #         conn,
    #         params=[municipality.department.name, min_cap, max_cap]
    #     )
    #     if len(df_services_reference) >= DEPT_SAMPLE:
    #         return _build_reference(df_services_reference, 'department')
    #     df_services_reference = pd.read_sql(
    #         ser_queries.QUERY_SERVICES_REFERENCE_NATIONAL, 
    #         conn,
    #         params=[min_cap, max_cap]
    #     )
    #     return _build_reference(df_services_reference, 'national')
    # finally:
    #     conn.close()

@staticmethod
def _build_reference(df, source):
    return MarketReference(
        source=source,
        sample_size=len(df),
        median_price_mbps=float(df["VLR_MBPS"].median()),
        mean_price_mbps=float(df["VLR_MBPS"].mean()),
        std_price_mbps=float(df["VLR_MBPS"].std())
    )
