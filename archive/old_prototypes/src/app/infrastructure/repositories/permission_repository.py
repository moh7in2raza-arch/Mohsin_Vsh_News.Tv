class PermissionRepository:
    def __init__(self, conn):
        self.conn = conn

    def codes_for_user(self, user_id: int) -> frozenset:
        rows = self.conn.execute(
            """SELECT DISTINCT p.code
               FROM user_roles ur
               JOIN role_permissions rp ON rp.role_id = ur.role_id
               JOIN permissions p ON p.id = rp.permission_id
               WHERE ur.user_id = %s""",
            (user_id,),
        ).fetchall()
        return frozenset(r[0] for r in rows)
    