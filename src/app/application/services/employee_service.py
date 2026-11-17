from __future__ import annotations

from src.app.domain.hr.employee import Employee


class EmployeeService:
    def __init__(self, employee_repository):
        self._employee_repository = employee_repository

    def create_employee(self, employee: Employee) -> Employee:
        employee.validate()
        self._employee_repository.add(employee)
        return employee

    def update_employee(self, employee: Employee) -> Employee:
        employee.validate()
        self._employee_repository.update(employee)
        return employee

    def delete_employee(self, employee_id: str) -> None:
        self._employee_repository.delete(employee_id)

    def get_employee(self, employee_id: str) -> Employee | None:
        return self._employee_repository.get(employee_id)

    def list_employees(self) -> list[Employee]:
        return self._employee_repository.list_all()

    def employee_exists(self, employee_id: str) -> bool:
        employee = self._employee_repository.get(employee_id)
        return employee is not None
    