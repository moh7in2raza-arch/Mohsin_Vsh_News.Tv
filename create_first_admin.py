from getpass import getpass
from argon2 import PasswordHasher
from src.app.infrastructure.database.connection import get_connection

print("\n===== ERP FIRST ADMIN ACCOUNT SETUP =====")

username = input("Enter username [admin]: ").strip() or "admin"
full_name = input("Enter administrator full name: ").strip()

if not full_name:
    raise SystemExit("Full name is required.")

password = getpass("Enter your password: ")
confirm = getpass("Confirm your password: ")

if password != confirm:
    raise SystemExit("Passwords do not match.")

if len(password) < 12:
    raise SystemExit("Password must contain at least 12 characters.")

password_hash = PasswordHasher().hash(password)

with get_connection() as conn:
    with conn.transaction():
        if conn.execute(
            "SELECT 1 FROM users WHERE username = %s", (username,)
        ).fetchone():
            raise SystemExit("Username already exists.")

        role = conn.execute(
            "SELECT id FROM roles WHERE name = 'Admin'"
        ).fetchone()

        if not role:
            raise SystemExit("Admin role not found.")

        user_id = conn.execute(
            """
            INSERT INTO users
                (username, full_name, password_hash, is_active,
                 must_change_password)
            VALUES (%s, %s, %s, TRUE, TRUE)
            RETURNING id
            """,
            (username, full_name, password_hash)
        ).fetchone()[0]

        conn.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
            (user_id, role[0])
        )

print("\nADMIN ACCOUNT CREATED SUCCESSFULLY")
print("Username:", username)
print("User ID:", user_id)
print("Role: Admin")
