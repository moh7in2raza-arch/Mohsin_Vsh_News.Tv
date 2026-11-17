import re
from pathlib import Path

from src.app.infrastructure.database.connection import get_connection

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_NAME = re.compile(r"^(\d{4})_.+\.sql$")


def _discover() -> list[tuple[int, Path]]:
    found = []
    for path in MIGRATIONS_DIR.glob("*.sql"):
        match = _NAME.match(path.name)
        if match:
            found.append((int(match.group(1)), path))
    return sorted(found)


def migrate() -> list[str]:
    """Apply every migration newer than the recorded version."""
    applied = []
    with get_connection() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS schema_version (
                   version    INTEGER PRIMARY KEY,
                   name       TEXT NOT NULL,
                   applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"""
        )
        conn.commit()
        current = conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM schema_version"
        ).fetchone()[0]
        for version, path in _discover():
            if version <= current:
                continue
            with conn.transaction():
                conn.execute(path.read_text(encoding="utf-8-sig"))
                conn.execute(
                    "INSERT INTO schema_version (version, name) VALUES (%s, %s)",
                    (version, path.name),
                )
            applied.append(path.name)
    return applied
