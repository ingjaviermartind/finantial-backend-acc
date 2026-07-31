import pyodbc
import pandas as pd
from Backend import models

from Backend.dtos.MarketReference import MarketReference

from Backend.sql import ser_queries
from Backend.sql.database import engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


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
