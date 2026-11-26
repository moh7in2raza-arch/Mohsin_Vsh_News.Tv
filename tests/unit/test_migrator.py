from contextlib import contextmanager

import pytest

from src.app.infrastructure.database import migrator


def test_backup_uses_separate_backup_credentials(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_HOST", "db-host")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "app-user")
    monkeypatch.setenv("DB_PASSWORD", "app-password")
    monkeypatch.setenv("DB_BACKUP_USER", "backup-user")
    monkeypatch.setenv("DB_BACKUP_PASSWORD", "backup-password")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(migrator.shutil, "which", lambda _: "pg_dump")
    captured = {}

    def run(command, **kwargs):
        captured["command"] = command
        captured["env"] = kwargs["env"]
        output_path = command[command.index("--file") + 1]
        with open(output_path, "wb") as backup:
            backup.write(b"custom-format-dump")

    monkeypatch.setattr(migrator.subprocess, "run", run)

    backup_path = migrator._backup_database()

    assert backup_path.read_bytes() == b"custom-format-dump"
    assert captured["command"][captured["command"].index("--username") + 1] == (
        "backup-user"
    )
    assert captured["env"]["PGPASSWORD"] == "backup-password"
    assert "backup-password" not in captured["command"]


class _Result:
    def __init__(self, value):
        self._value = value

    def fetchone(self):
        return (self._value,)


class _Connection:
    def __init__(self, version):
        self.version = version
        self.statements = []

    def execute(self, statement, params=None):
        self.statements.append(statement)
        if "to_regclass" in statement:
            return _Result(True)
        if "MAX(version)" in statement:
            return _Result(self.version)
        return _Result(None)

    @contextmanager
    def transaction(self):
        yield

    def commit(self):
        self.statements.append("COMMIT")


def test_migration_backs_up_before_ddl(monkeypatch, tmp_path):
    migration_file = tmp_path / "0012_test.sql"
    migration_file.write_text("SELECT 12", encoding="utf-8")
    conn = _Connection(version=11)

    @contextmanager
    def connection_context():
        yield conn

    events = []
    monkeypatch.setattr(migrator, "get_connection", connection_context)
    monkeypatch.setattr(migrator, "_discover", lambda: [(12, migration_file)])
    monkeypatch.setattr(
        migrator, "_backup_database", lambda: events.append("backup")
    )
    original_execute = conn.execute

    def record_execute(statement, params=None):
        events.append(statement)
        return original_execute(statement, params)

    monkeypatch.setattr(conn, "execute", record_execute)

    assert migrator.migrate() == ["0012_test.sql"]
    assert events.index("backup") < next(
        index for index, event in enumerate(events)
        if "CREATE TABLE IF NOT EXISTS schema_version" in event
    )


def test_failed_backup_prevents_migration(monkeypatch, tmp_path):
    migration_file = tmp_path / "0012_test.sql"
    migration_file.write_text("SELECT 12", encoding="utf-8")
    conn = _Connection(version=11)

    @contextmanager
    def connection_context():
        yield conn

    monkeypatch.setattr(migrator, "get_connection", connection_context)
    monkeypatch.setattr(migrator, "_discover", lambda: [(12, migration_file)])

    def fail_backup():
        raise RuntimeError("backup unavailable")

    monkeypatch.setattr(migrator, "_backup_database", fail_backup)
    with pytest.raises(RuntimeError, match="backup unavailable"):
        migrator.migrate()

    assert not any(
        "CREATE TABLE IF NOT EXISTS schema_version" in statement
        or statement == "SELECT 12"
        for statement in conn.statements
    )

