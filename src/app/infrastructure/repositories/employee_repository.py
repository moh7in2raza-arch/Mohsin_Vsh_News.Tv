from decimal import Decimal
from contextlib import contextmanager

from src.app.domain.hr.employee import Employee
from src.app.infrastructure.database.connection import get_connection
from src.app.infrastructure.repositories._sql import (
    fetch_all,
    fetch_one,
)


class EmployeeRepository:
    def __init__(self, conn=None):
        self._external_conn = conn

    @contextmanager
    def _connection(self):
        if self._external_conn is not None:
            yield self._external_conn
        else:
            with get_connection() as conn:
                yield conn

    def add(self, employee: Employee) -> int:
        with self._connection() as conn:
            department_id = self._department_id(conn, employee.department)
            row = conn.execute(
                """
                INSERT INTO employees (
                    employee_code,
                    full_name,
                    email,
                    phone,
                    department_id,
                    joining_date,
                    status,
                    cnic,
                    designation,
                    salary
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    employee.employee_id,
                    employee.full_name,
                    employee.email,
                    employee.phone,
                    department_id,
                    employee.joining_date,
                    employee.status,
                    employee.cnic,
                    employee.designation,
                    employee.salary,
                ),
            ).fetchone()
            return row[0]

    def update(self, employee: Employee) -> None:
        with self._connection() as conn:
            department_id = self._department_id(conn, employee.department)
            conn.execute(
                """
                UPDATE employees
                SET
                    full_name = %s,
                    email = %s,
                    phone = %s,
                    department_id = %s,
                    joining_date = %s,
                    status = %s,
                    cnic = %s,
                    designation = %s,
                    salary = %s
                WHERE employee_code = %s
                """,
                (
                    employee.full_name,
                    employee.email,
                    employee.phone,
                    department_id,
                    employee.joining_date,
                    employee.status,
                    employee.cnic,
                    employee.designation,
                    employee.salary,
                    employee.employee_id,
                ),
            )

    def _department_id(self, conn, department_name: str) -> int | None:
        name = (department_name or "").strip()
        if not name:
            return None
        row = conn.execute(
            "SELECT id FROM departments WHERE name = %s",
            (name,),
        ).fetchone()
        if row is not None:
            return row[0]
        row = conn.execute(
            "INSERT INTO departments (code, name) VALUES (%s, %s) "
            "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name "
            "RETURNING id",
            (name[:50].upper().replace(" ", "_"), name),
        ).fetchone()
        return row[0]

    def delete(self, employee_id: str) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                DELETE FROM employees
                WHERE employee_code = %s
                """,
                (employee_id,),
            )

    def get(self, employee_id: str) -> Employee | None:
        with self._connection() as conn:
            row = fetch_one(
                conn,
                """
                SELECT
                    e.employee_code,
                    e.full_name,
                    e.cnic,
                    e.phone,
                    e.email,
                    d.name AS department,
                    e.designation,
                    e.joining_date,
                    e.salary,
                    e.status
                FROM employees e
                LEFT JOIN departments d ON d.id = e.department_id
                WHERE e.employee_code = %s
                """,
                (employee_id,),
            )

        if row is None:
            return None

        return Employee(
            employee_id=row["employee_code"],
            full_name=row["full_name"],
            cnic=row["cnic"] or "",
            phone=row["phone"] or "",
            email=row["email"] or "",
            department=row["department"] or "",
            designation=row["designation"] or "",
            joining_date=row["joining_date"],
            salary=Decimal(str(row["salary"] or 0)),
            status=row["status"] or "Active",
        )

    def list_all(self) -> list[dict]:
        with self._connection() as conn:
            return fetch_all(
                conn,
                """
                SELECT
                    e.employee_code,
                    e.full_name,
                    d.name AS department,
                    e.designation,
                    e.cnic,
                    e.phone,
                    e.joining_date,
                    e.salary,
                    e.status
                FROM employees e
                LEFT JOIN departments d ON d.id = e.department_id
                ORDER BY e.full_name
                """,
            )
    