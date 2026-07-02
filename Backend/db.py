"""Database helper-ներ ArmWork backend-ի համար։

Կոդը default աշխատում է SQLite-ով, որ local թեստը լինի շատ հեշտ։
SQL Server-ի կապը պահված է որպես optional ռեժիմ՝ ARMWORK_DB_TYPE=mssql։
"""

from datetime import date, datetime
from decimal import Decimal
import sqlite3

from config import Config

try:
    import pyodbc
except ImportError:  # pyodbc-ը պետք չէ local sqlite ռեժիմում։
    pyodbc = None


if pyodbc:
    DatabaseIntegrityError = (sqlite3.IntegrityError, pyodbc.IntegrityError)
else:
    DatabaseIntegrityError = (sqlite3.IntegrityError,)


def is_sqlite():
    """Վերադարձնում է True, եթե backend-ը աշխատում է SQLite ռեժիմով։"""
    return Config.DB_TYPE != "mssql"


def table_name(name):
    """Table-ի անունը վերադարձնում է տվյալ database engine-ին համապատասխան։"""
    if is_sqlite():
        return name
    return f"dbo.{name}"


def utc_now_sql():
    """UpdatedAt դաշտը թարմացնելու SQL ֆունկցիա ըստ database-ի։"""
    if is_sqlite():
        return "CURRENT_TIMESTAMP"
    return "SYSUTCDATETIME()"


def get_connection():
    """Բացում է database կապը՝ SQLite կամ SQL Server։"""
    if is_sqlite():
        connection = sqlite3.connect(Config.SQLITE_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    if pyodbc is None:
        raise RuntimeError(
            "SQL Server ռեժիմի համար պետք է տեղադրել pyodbc-ը կամ օգտագործել default sqlite ռեժիմը։"
        )

    connection_string = (
        f"DRIVER={{{Config.DB_DRIVER}}};"
        f"SERVER={Config.DB_SERVER};"
        f"DATABASE={Config.DB_NAME};"
        f"UID={Config.DB_USER};"
        f"PWD={Config.DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)


def to_json_value(value):
    """Database արժեքները դարձնում է JSON-ի համար հարմար արժեքներ։"""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def row_to_dict(cursor, row):
    """Database row-ը վերածում է սովորական dict-ի։"""
    if row is None:
        return None

    columns = [column[0] for column in cursor.description]
    return {column: to_json_value(value) for column, value in zip(columns, row)}


def rows_to_dicts(cursor):
    """cursor-ի բոլոր row-երը վերածում է dict-երի list-ի։"""
    columns = [column[0] for column in cursor.description]
    return [
        {column: to_json_value(value) for column, value in zip(columns, row)}
        for row in cursor.fetchall()
    ]
