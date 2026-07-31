from sqlalchemy import create_engine
from urllib.parse import quote_plus

params = quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.142.16.246\\accdwh;"
    "DATABASE=Azteca_Staging;"
    "Trusted_Connection=yes;"
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}",
    pool_pre_ping=True,
    fast_executemany=True,
)