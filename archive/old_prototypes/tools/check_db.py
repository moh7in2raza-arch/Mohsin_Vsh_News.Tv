import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg

print(".env exists:", Path(".env").exists())
load_dotenv()

try:
    conn = psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
except KeyError as e:
    print("Missing setting in .env:", e)
    raise SystemExit(1)
except Exception as e:
    print("Connection FAILED:", type(e).__name__)
    print(str(e).strip().splitlines()[0])
    raise SystemExit(1)

row = conn.execute("select current_user, current_database()").fetchone()
print("Connected as:", row)
tables = [r[0] for r in conn.execute(
    "select tablename from pg_tables where schemaname = 'public' order by 1")]
print("Tables in public:", tables)
conn.close()
