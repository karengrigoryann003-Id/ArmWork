"""ArmWork backend-ի կարգավորումներ։

Կոնֆիգը կարդում է Backend/.env ֆայլից, որպեսզի գաղտնաբառերը կոդի մեջ չպահենք։
Քո ուզած SQL Server ռեժիմի համար .env-ում դիր ARMWORK_DB_TYPE=mssql։
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def load_env_file():
    """Կարդում է պարզ KEY=VALUE տողերը .env ֆայլից, եթե ֆայլը կա։"""
    if not ENV_FILE.exists():
        return

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file()


class Config:
    # Local fallback-ը sqlite է։ SQL Server-ի համար Backend/.env-ում գրիր ARMWORK_DB_TYPE=mssql։
    DB_TYPE = os.getenv("ARMWORK_DB_TYPE", "sqlite").lower()

    # SQLite fallback database ֆայլը։ SQL Server ռեժիմում սա չի օգտագործվում։
    SQLITE_PATH = os.getenv("ARMWORK_SQLITE_PATH", str(BASE_DIR / "armwork.db"))

    # Քո SQL Server-ի տվյալները՝ localhost,1433 / SA / ArmWork։
    DB_SERVER = os.getenv("ARMWORK_DB_SERVER", "localhost,1433")
    DB_NAME = os.getenv("ARMWORK_DB_NAME", "ArmWork")
    DB_USER = os.getenv("ARMWORK_DB_USER", "SA")
    DB_PASSWORD = os.getenv("ARMWORK_DB_PASSWORD", "")
    DB_DRIVER = os.getenv("ARMWORK_DB_DRIVER", "ODBC Driver 18 for SQL Server")

    # 0.0.0.0 նշանակում է՝ նույն Wi-Fi-ի սարքերն էլ կարող են բացել backend-ը։
    API_HOST = os.getenv("ARMWORK_API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("ARMWORK_API_PORT", "5050"))
    DEBUG = os.getenv("ARMWORK_DEBUG", "true").lower() == "true"
