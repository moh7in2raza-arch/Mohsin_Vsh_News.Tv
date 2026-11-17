from __future__ import annotations

from typing import Dict

from src.app.domain.hr.employee import Employee


class EmployeeRepository:
    def __init__(self):
        self._employees: Dict[str, Employee] = {}

    def add(self, employee: Employee) -> None:
        self._employees[employee.employee_id] = employee

    def update(self, employee: Employee) -> None:
        self._employees[employee.employee_id] = employee

    def delete(self, employee_id: str) -> None:
        self._employees.pop(employee_id, None)

    def get(self, employee_id: str) -> Employee | None:
        return self._employees.get(employee_id)

    def list_all(self) -> list[Employee]:
        return list(self._employees.values())
    