import pandas as pd
from Backend import models

from Backend.dtos.MarketReference import MarketReference

from Backend.sql import ser_queries
from Backend.sql.database import engine
from sqlalchemy import text, bindparam
from sqlalchemy.exc import SQLAlchemyError

from Backend import models

from django.db.models import F

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
def get_clients() : 
    try:
        query = text(ser_queries.QUERY_ACTIVE_CLIENTS)
        df_active_clients = pd.read_sql(
            query,
            engine
        )
        clients = (
            df_active_clients
            .groupby("NIT", sort=True)["RAZON_SOCIAL"]
            .apply(
                lambda names: sorted(
                    {
                        name.strip()
                        for name in names
                        if pd.notna(name) and str(name).strip()
                    }
                )
            ).reset_index(name="business_names")
        )
        return {
            "success": True,
            "data": clients.to_dict(
                orient="records"
            )
        }
    except SQLAlchemyError as e:
        print("SQLALCHEMY ERROR:", repr(e))
        return {
            "success": False,
            "code": "DATABASE_ERROR",
            "message": "Error consultando la base de datos."
        }
    except Exception as e:
        print("UNKNOWN ERROR:", type(e), repr(e))
        return {
            "success": False,
            "code": "UNKNOWN_ERROR",
            "message": "Error inesperado."
        }


@staticmethod
def get_services(filters):
    try:
        municipalities = models.Municipality.objects.filter(id__in=filters.municipalities)
        danes = list(
            municipalities.values_list(
                "dane",
                flat=True
            )
        )
        municipality_data = {
            str(m["dane"]).zfill(5): {
                "unprofitable": m["unprofitable"],
                "node": m["node"],
                "region": m["region__name"],
            }
            for m in municipalities.values(
                "dane",
                "unprofitable",
                "node",
                "region__name",
            )
        }
        params = {
            "capacity_min": filters.capacity_min,
            "capacity_max": filters.capacity_max,
            "danes": danes,
            "filter_product_family": (1 if filters.product_families else 0),
            "product_families": filters.product_families,
            "filter_product": 1 if filters.products else 0,
            "products": filters.products,
            "filter_plan": 1 if filters.plans else 0,
            "plans": filters.plans,
            "filter_client": 1 if filters.clients else 0,
            "clients": filters.clients,
            "filter_subsegment": (1 if filters.subsegments else 0),
            "subsegments": filters.subsegments,
        }
        expanding_params = [
            "danes",
            "product_families",
            "products",
            "plans",
            "clients",
            "subsegments",
        ]
        query = text(ser_queries.QUERY_ACTIVE_SERVICES_V2).bindparams(
            *[
                bindparam(param, expanding=True)
                for param in expanding_params
            ]
        )
        df_active_services = pd.read_sql(
            query,
            engine,
            params=params
        )
        df_active_services = (
            df_active_services
            .astype(object)
            .where(
                pd.notna(df_active_services),
                None
            )
        )
        df_active_services["DANE_JOIN"] = (
            df_active_services["Codigo DANE"]
            .astype(str)
            .str.strip()
            .str.zfill(5)
        )
        df_active_services["unprofitable"] = (
            df_active_services["DANE_JOIN"]
            .map(
                lambda dane: municipality_data.get(
                    dane,
                    {}
                ).get("unprofitable", False)
            )
        )
        df_active_services["node"] = (
            df_active_services["DANE_JOIN"]
            .map(
                lambda dane: municipality_data.get(
                    dane,
                    {}
                ).get("node")
            )
        )
        df_active_services["region"] = (
            df_active_services["DANE_JOIN"]
            .map(
                lambda dane: municipality_data.get(
                    dane,
                    {}
                ).get("region")
            )
        )
        df_active_services["region"] = (
            df_active_services["DANE_JOIN"]
            .map(
                lambda dane: municipality_data.get(
                    dane,
                    {}
                ).get("region")
            )
        )
        df_active_services.drop(columns=["DANE_JOIN"], inplace=True)
        df_active_services["Producto"] = (
            df_active_services["Producto"]
            .str.title()
            .str.replace("Id", "ID", regex=False)
            .str.replace("Ip", "IP", regex=False)
            .str.replace("Iru", "IRU", regex=False)
            .str.replace("Uk", "UK", regex=False)
            .str.replace("Ba", "BA", regex=False)
            .str.replace("De ", "de ", regex=False)
            .str.replace("Sin ", "sin ",regex=False)
        )
        
        return {
            "success": True,
            "data": df_active_services.to_dict(
                orient="records"
            )
        }
    except SQLAlchemyError as e:
        print("SQLALCHEMY ERROR:", repr(e))
        return {
            "success": False,
            "code": "DATABASE_ERROR",
            "message": "Error consultando la base de datos."
        }
    except Exception as e:
        print("UNKNOWN ERROR:", type(e), repr(e))
        return {
            "success": False,
            "code": "UNKNOWN_ERROR",
            "message": "Error inesperado."
        }
    
@staticmethod
def get_services_by_municipality(key, min_cap = 10):
    try:
        municipality = models.Municipality.objects.get(id=key)
        df_active_services = pd.read_sql(
            text(ser_queries.QUERY_ACTIVE_SERVICES),
            engine,
            params={
                "min_cap": min_cap,
                "dane": municipality.dane
            }
        )
        clients = pd.DataFrame(
            models.Client.objects.values(
                'identification_number',
                'verification_number',
                'name',
                'subsegment__name'
            )
        )
        clients = clients.rename(
            columns={
                'subsegment__name': 'subsegment'
            }
        )
        clients['NIT'] = clients.apply(
            lambda row: (
                f"{int(row['identification_number'])}-{int(row['verification_number'])}"
                if pd.notna(row['verification_number'])
                else str(int(row['identification_number']))
            ),
            axis=1
        )
        df_active_services = df_active_services.merge(
            clients[['NIT', 'name', 'subsegment']],
            on='NIT',
            how='left'
        )
        df_active_services["subsegment"] = (
            df_active_services["subsegment"].fillna("Sin segmentar")
        )
        df_active_services['Razón Social'] = (
            df_active_services['name']
            .combine_first(df_active_services['Razón Social'])
        )
        capacity = pd.to_numeric(
            df_active_services['CAPACIDADBPS'],
            errors='coerce'
        )
        df_active_services['Rango Capacidad'] = capacity.apply(
            get_capacity_group
        )
        df_active_services.drop(columns=['name'], inplace=True)
        df_active_services.drop(columns=['CAPACIDADBPS'], inplace=True)

        df_active_services['Producto'] = df_active_services['Producto'].str.title().str.replace('Id', 'ID', regex=False).str.replace('Ip', 'IP', regex=False).str.replace('Iru', 'IRU', regex=False).str.replace('Uk', 'UK', regex=False).str.replace('Ba', 'BA', regex=False)

        return {
            "success": True,
            "data": df_active_services.to_dict(orient="records")
        }

    except models.Municipality.DoesNotExist:
        return {
            "success": False,
            "code": "MUNICIPALITY_NOT_FOUND",
            "message": "El municipio no existe"
        }

    except SQLAlchemyError as e:
        print("SQLALCHEMY ERROR:", repr(e))

        return {
            "success": False,
            "code": "DATABASE_ERROR",
            "message": "Error consultando la base de datos."
        }

    except Exception as e:
        print("UNKNOWN ERROR:", type(e), repr(e))

        return {
            "success": False,
            "code": "UNKNOWN_ERROR",
            "message": "Error inesperado."
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
