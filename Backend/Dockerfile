FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# SQL Server-ին միանալու համար container-ի մեջ տեղադրում ենք Microsoft ODBC Driver 18-ը։
RUN apt-get update     && apt-get install -y --no-install-recommends         apt-transport-https         ca-certificates         curl         gcc         g++         gnupg         unixodbc-dev     && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg     && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list     && apt-get update     && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18     && apt-get clean     && rm -rf /var/lib/apt/lists/*

COPY Backend/requirements-sqlserver.txt /app/Backend/requirements-sqlserver.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel     && pip install --no-cache-dir -r /app/Backend/requirements-sqlserver.txt

COPY Backend /app/Backend
COPY Frontend /app/Frontend
COPY DataBase /app/DataBase

WORKDIR /app/Backend

EXPOSE 5050

# Container-ը start անելիս նախ ստեղծում/թարմացնում է table-ները, հետո բացում է API server-ը։
CMD ["sh", "-c", "python scripts/wait_for_database.py && python scripts/init_db.py && python scripts/seed_test_data.py && python app.py"]
