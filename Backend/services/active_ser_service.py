import pyodbc
import pandas as pd
from Backend import models

from Backend.dtos.MarketReference import MarketReference

from Backend.sql import ser_queries

@staticmethod
def get_services_by_municipality(key, min_cap = 10):
    municipality = models.Municipality.objects.get(id=key)
    conn = pyodbc.connect(
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=10.142.16.246\accdwh;"
        r"DATABASE=Azteca_Staging;"
        r"Trusted_Connection=yes;"
    )
    try:
        df_active_services = pd.read_sql(
            ser_queries.QUERY_ACTIVE_SERVICES, 
            conn,
            params=[min_cap,municipality.dane]
        )
    finally:
        conn.close()
    return df_active_services.to_dict(orient="records")

@staticmethod
def get_services_reference_by_municipality(municipality):
    MIN_SAMPLE = 5
    DEPT_SAMPLE = 5

    conn = pyodbc.connect(
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=10.142.16.246\accdwh;"
        r"DATABASE=Azteca_Staging;"
        r"Trusted_Connection=yes;"
    )
    try:
        df_services_reference = pd.read_sql(
            ser_queries.QUERY_SERVICES_REFERENCE_MUN, 
            conn,
            params=[municipality.dane]
        )
        if len(df_services_reference) >= MIN_SAMPLE:
            return _build_reference(df_services_reference,'municipality')
        df_services_reference = pd.read_sql(
            ser_queries.QUERY_SERVICES_REFERENCE_DEPT, 
            conn,
            params=[municipality.department.name]
        )
        if len(df_services_reference) >= DEPT_SAMPLE:
            return _build_reference(df_services_reference, 'department')
        df_services_reference = pd.read_sql(
            ser_queries.QUERY_SERVICES_REFERENCE_NATIONAL, 
            conn
        )
        return _build_reference(df_services_reference, 'national')
    finally:
        conn.close()

@staticmethod
def _build_reference(df, source):
    return MarketReference(
        source=source,
        sample_size=len(df),
        median_price_mbps=float(df["VLR_MBPS"].median()),
        mean_price_mbps=float(df["VLR_MBPS"].mean()),
        std_price_mbps=float(df["VLR_MBPS"].std())
    )
