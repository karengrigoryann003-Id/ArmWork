# ArmWork Backend

ArmWork-ի Python/Flask backend-ը կապում է frontend-ը database-ի հետ։

Կարևոր ճարտարապետություն՝

```text
GitHub Pages / Browser → Python Backend API → SQL Server ArmWork database
```

Frontend-ը չի կարող ուղիղ SQL Server-ին միանալ, դրա համար backend-ը միշտ պետք է միացված լինի։

## SQL Server local database ռեժիմ

Քո նշած server-ը՝

```text
Server: localhost,1434
User: SA
Database: ArmWork
```

### 1. Պատրաստել Python 3.12 environment-ը

`pyodbc`-ը քո Python 3.14-ի վրա խնդիր է տալիս, դրա համար SQL Server ռեժիմի համար օգտագործիր Python 3.12։

```bash
cd "/Users/karengrigoryan/Documents/My first Project /Backend"
rm -rf .venv
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-sqlserver.txt
```

Եթե Python 3.12 դեռ չունես՝

```bash
brew install python@3.12
```

Եթե SQL Server ODBC driver չունես՝

```bash
brew install unixodbc
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18
```

### 2. Ստեղծել Backend/.env ֆայլը

```bash
cp .env.example .env
```

Բացիր `.env` ֆայլը և փոխիր միայն գաղտնաբառը՝

```text
ARMWORK_DB_PASSWORD=ՔՈ_SA_PASSWORDԸ
```

### 3. Ստեղծել ArmWork database-ը SQL Server-ում

```bash
python scripts/init_db.py
```

### 4. Միացնել backend-ը

```bash
python app.py
```

Backend-ը կաշխատի՝

```text
http://127.0.0.1:5050/
```

Նույն Wi-Fi-ի սարքերից բացելու համար գտիր Mac-ի IP-ն՝

```bash
ipconfig getifaddr en0
```

Հետո բացիր՝

```text
http://ՔՈ_MAC_IP:5050/
```

## GitHub Pages-ից թեստ

GitHub Pages-ը միայն frontend է։ Որպեսզի GitHub-ից բացված կայքը աշխատի քո Mac-ի backend-ի հետ, պետք է backend-ը public URL ունենա։ Ամենահեշտը ngrok-ն է։

```bash
brew install ngrok
ngrok http 5050
```

Ngrok-ը կտա օրինակ՝

```text
https://abc.ngrok-free.app
```

Այդ URL-ը դիր `Frontend/js/config.js` ֆայլում՝

```js
window.ARMWORK_CONFIG.API_BASE_URL = "https://abc.ngrok-free.app/api";
```

Հետո push արա GitHub, բացիր GitHub Pages-ի link-ը և կկարողանաս գրանցվել, login լինել, username որոնել ու message ուղարկել։

## Local SQLite fallback

Եթե ուզում ես արագ թեստ Python 3.14-ով առանց SQL Server-ի՝

```bash
cd "/Users/karengrigoryan/Documents/My first Project /Backend"
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python app.py
```

## Docker workflow՝ SQL Server + Backend

Այս տարբերակը բարձրացնում է SQL Server-ը և Python backend-ը Docker-ով։ Database տվյալները պահվում են Docker volume-ում՝ `armwork_sql_data`, այսինքն՝ container-ը restart անելուց չեն կորում։

> Նշում Mac M3-ի համար․ Microsoft SQL Server container image-ը պաշտոնապես x86-64 Linux host-երի համար է։ Mac M3-ում Docker Desktop-ը այն աշխատացնում է amd64 emulation-ով, դրա համար Docker Desktop-ի settings-ում միացրու Rosetta/x86 emulation-ը, եթե container-ը չբարձրանա։

### 1. Պատրաստել .env ֆայլը

```bash
cd "/Users/karengrigoryan/Documents/My first Project "
cp .env.docker.example .env
```

Եթե ուզում ես, `.env`-ում փոխիր password-ը՝

```text
MSSQL_SA_PASSWORD=ՔՈ_ՈՒԺԵՂ_PASSWORDԸ
```

### 2. Բարձրացնել SQL Server-ը և backend-ը

```bash
docker compose up --build
```

Բացիր՝

```text
http://127.0.0.1:5050/
```

### 3. GitHub Pages-ից կապել backend-ին

Եթե ուզում ես GitHub Pages-ի link-ից թեստել, backend-ը public արա ngrok-ով՝

```bash
ngrok http 5050
```

Ngrok-ի URL-ը դիր `Frontend/js/config.js`-ում՝

```js
window.ARMWORK_CONFIG.API_BASE_URL = "https://ՔՈ_NGROK_URL.ngrok-free.app/api";
```

Հետո commit/push արա GitHub։

## Ստանդարտ թեստ՝ Docker + GitHub Pages

Այս flow-ը քո ուզած տարբերակն է՝ Docker-ում պահվում է backend/database-ը, իսկ GitHub Pages-ում բացվում է frontend-ը։

### 1. Docker-ը բարձրացնել

```bash
cd "/Users/karengrigoryan/Documents/My first Project "
cp .env.docker.example .env
docker compose up --build
```

Backend-ը կբացվի՝

```text
http://127.0.0.1:5050/
```

Docker start-ի ժամանակ ավտոմատ աշխատում են՝

```text
python scripts/wait_for_database.py
python scripts/init_db.py
python scripts/seed_test_data.py
python app.py
```

### 2. Test user-ներով local ստուգել

| Role | Username | Password |
| --- | --- | --- |
| Client / Գործատու | `client_demo` | `ArmWork123!` |
| Freelancer | `freelancer_demo` | `ArmWork123!` |

### 3. Backend-ը ինտերնետից հասանելի դարձնել

Նոր Terminal-ում՝

```bash
ngrok http 5050
```

Օրինակ կստանաս՝

```text
https://abc.ngrok-free.app
```

### 4. GitHub Pages frontend-ը կապել backend-ին

Բացիր `Frontend/js/config.js` և դիր՝

```js
window.ARMWORK_CONFIG.API_BASE_URL = "https://abc.ngrok-free.app/api";
```

### 5. Commit / push

```bash
cd "/Users/karengrigoryan/Documents/My first Project "
git init
git add .
git commit -m "Prepare ArmWork GitHub Pages test setup"
git branch -M main
git remote add origin ՔՈ_GITHUB_REPO_URL
git push -u origin main
```

GitHub Pages-ում source ընտրիր repository-ի branch-ը, հետո բացիր frontend-ը։ Եթե repo-ում root-ից է publish լինում, հասցեն սովորաբար կլինի՝

```text
https://ՔՈ_USERNAME.github.io/ՔՈ_REPO_NAME/Frontend/
```

Եթե ngrok-ի URL-ը փոխվի, պետք է նոր URL-ը դնես `Frontend/js/config.js`-ում և նորից push անես։
