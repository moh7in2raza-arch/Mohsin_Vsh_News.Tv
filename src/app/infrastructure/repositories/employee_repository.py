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
            row = conn.execute(
                """
                INSERT INTO employees (
                    employee_code,
                    full_name,
                    email,
                    phone,
                    joining_date,
                    status,
                    cnic,
                    designation,
                    salary
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    employee.employee_id,
                    employee.full_name,
                    employee.email,
                    employee.phone,
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
            conn.execute(
                """
                UPDATE employees
                SET
                    full_name = %s,
                    email = %s,
                    phone = %s,
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
                    employee.joining_date,
                    employee.status,
                    employee.cnic,
                    employee.designation,
                    employee.salary,
                    employee.employee_id,
                ),
            )

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
                    employee_code,
                    full_name,
                    cnic,
                    phone,
                    email,
                    designation,
                    joining_date,
                    salary,
                    status
                FROM employees
                WHERE employee_code = %s
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
            department="",
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
                    employee_code,
                    full_name,
                    email,
                    phone,
                    designation,
                    salary,
                    status,
                    joining_date
                FROM employees
                ORDER BY full_name
                """,
            )
    