:: -d for detached -> runs in background and doesn't stay open in terminal
docker run -d --name skill-project-redisvl -p 6379:6379 -it redis/redis-stack-server
docker run -d --name skill-project-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=skilldb -p 5432:5432 postgres:16

IF NOT EXIST .venv (
    py -3.11 -m venv .venv
)
CALL .venv\Scripts\activate
python -m pip install -r pythonRequirements.txt

python setupRedis.py
python setupPostgress.py

pause