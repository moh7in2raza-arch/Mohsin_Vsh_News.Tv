import os
import sys
from pathlib import Path

import psycopg
from dotenv import find_dotenv, load_dotenv


def _load_env() -> None:
    if getattr(sys, "frozen", False):          # installed .exe: .env sits beside it
        load_dotenv(Path(sys.executable).parent / ".env")
    else:
        load_dotenv(find_dotenv(usecwd=True))


def get_connection() -> psycopg.Connection:
    """Open a PostgreSQL connection using settings from .env."""
    _load_env()
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