class AuditRepository:
    def __init__(self, conn):
        self.conn = conn

    def record(self, user_id, action, entity=None, entity_id=None) -> None:
        self.conn.execute(
            "INSERT INTO audit_log (user_id, action, entity, entity_id) VALUES (%s, %s, %s, %s)",
            (user_id, action, entity, entity_id),
        )