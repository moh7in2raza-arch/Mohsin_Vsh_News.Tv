import os

import psycopg
from dotenv import load_dotenv


def get_connection() -> psycopg.Connection:
    """Open a PostgreSQL connection using settings from .env."""
    load_dotenv()
    try:
        return psycopg.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        )
    except KeyError as missing:
        raise RuntimeError(f"Missing setting in .env: {missing}") from None
