"""Docker-ի մեջ սպասում է, մինչև SQL Server-ը պատրաստ լինի։"""

from pathlib import Path
import sys
import time

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from config import Config
from db import is_sqlite


MAX_ATTEMPTS = 60
WAIT_SECONDS = 2


def wait_for_mssql():
    """Փորձում է միանալ SQL Server master database-ին, մինչև server-ը պատրաստ լինի։"""
    try:
        import pyodbc
    except ImportError as error:
        raise RuntimeError("Docker SQL Server ռեժիմի համար pyodbc-ը պարտադիր է։") from error

    connection_string = (
        f"DRIVER={{{Config.DB_DRIVER}}};"
        f"SERVER={Config.DB_SERVER};"
        "DATABASE=master;"
        f"UID={Config.DB_USER};"
        f"PWD={Config.DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with pyodbc.connect(connection_string, timeout=5):
                print("SQL Server-ը պատրաստ է։")
                return
        except pyodbc.Error:
            print(f"Սպասում ենք SQL Server-ին... փորձ {attempt}/{MAX_ATTEMPTS}")
            time.sleep(WAIT_SECONDS)

    raise RuntimeError("SQL Server-ին միանալ չստացվեց։ Ստուգիր Docker container logs-ը։")


def main():
    if is_sqlite():
        print("SQLite ռեժիմ է, database wait պետք չէ։")
        return

    wait_for_mssql()


if __name__ == "__main__":
    main()
