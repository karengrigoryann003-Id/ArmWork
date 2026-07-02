"""ArmWork database-ը ստեղծելու helper։

Default ռեժիմը SQLite է և աշխատում է Python 3.14-ով առանց լրացուցիչ driver-ի։
Օգտագործում՝
    python scripts/init_db.py

SQL Server ռեժիմի համար՝
    export ARMWORK_DB_TYPE=mssql
    export ARMWORK_DB_PASSWORD='ՔՈ_SA_PASSWORD'
    python scripts/init_db.py
"""

from pathlib import Path
import sqlite3
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from config import Config
from db import is_sqlite

ROOT = Path(__file__).resolve().parents[2]
SQLITE_SCHEMA = ROOT / "DataBase" / "database_sqlite.sql"
MSSQL_SCHEMA = ROOT / "DataBase" / "database.sql"


def split_batches(sql_text):
    """SQL Server-ի GO բաժանարարներով script-ը կտրում է առանձին batch-երի։"""
    batches = []
    current_lines = []

    for line in sql_text.splitlines():
        if line.strip().upper() == "GO":
            batch = "\n".join(current_lines).strip()
            if batch:
                batches.append(batch)
            current_lines = []
        else:
            current_lines.append(line)

    last_batch = "\n".join(current_lines).strip()
    if last_batch:
        batches.append(last_batch)

    return batches


def init_sqlite():
    """Ստեղծում է local SQLite database-ը։"""
    db_path = Path(Config.SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql_text = SQLITE_SCHEMA.read_text(encoding="utf-8")

    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql_text)

    print(f"ArmWork SQLite database-ը պատրաստ է՝ {db_path}")


def init_mssql():
    """Ստեղծում է SQL Server database-ը, եթե ընտրել ես mssql ռեժիմը։"""
    try:
        import pyodbc
    except ImportError as error:
        raise RuntimeError("SQL Server ռեժիմի համար տեղադրիր pyodbc-ը։") from error

    connection_string = (
        f"DRIVER={{{Config.DB_DRIVER}}};"
        f"SERVER={Config.DB_SERVER};"
        "DATABASE=master;"
        f"UID={Config.DB_USER};"
        f"PWD={Config.DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )

    sql_text = MSSQL_SCHEMA.read_text(encoding="utf-8")

    with pyodbc.connect(connection_string, autocommit=True) as conn:
        cursor = conn.cursor()
        for batch in split_batches(sql_text):
            cursor.execute(batch)

    print("ArmWork SQL Server database schema-ը ստեղծվեց կամ արդեն գոյություն ուներ։")


def main():
    if is_sqlite():
        init_sqlite()
    else:
        init_mssql()


if __name__ == "__main__":
    main()
