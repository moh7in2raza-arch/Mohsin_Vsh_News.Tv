from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True)
class Employee:
    employee_id: str
    full_name: str
    cnic: str
    phone: str
    email: str

    department: str
    designation: str

    joining_date: date
    salary: Decimal

    status: str

    def validate(self) -> None:
        if not self.employee_id.strip():
            raise ValueError("Employee ID is required.")

        if not self.full_name.strip():
            raise ValueError("Full name is required.")

        if not self.cnic.strip():
            raise ValueError("CNIC is required.")

        if not self.department.strip():
            raise ValueError("Department is required.")

        if not self.designation.strip():
            raise ValueError("Designation is required.")

        if self.salary < 0:
            raise ValueError("Salary cannot be negative.")

    @property
    def is_active(self) -> bool:
        return self.status.lower() == "active"
    