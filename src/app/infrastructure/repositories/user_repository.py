from src.app.infrastructure.database.connection import get_connection


class UserRepository:

    def get_by_username(self, username: str):

        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        id,
                        username,
                        password_hash,
                        is_active,
                        must_change_password
                    FROM users
                    WHERE username = %s
                    """,
                    (username,)
                )

                row = cur.fetchone()

                if not row:
                    return None

                return {
                    "id": row[0],
                    "username": row[1],
                    "password_hash": row[2],
                    "is_active": row[3],
                    "must_change_password": row[4],
                }
                