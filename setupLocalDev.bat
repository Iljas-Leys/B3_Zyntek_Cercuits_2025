@echo off

docker run -d --name skill-project-redisvl -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
docker run -d --name skill-project-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=mydb -p 5432:5432 postgres:16

IF NOT EXIST .venv (
    py -3.11 -m venv .venv
)

CALL .venv\Scripts\activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r pythonRequirements.txt

python setupRedis.py

pause
