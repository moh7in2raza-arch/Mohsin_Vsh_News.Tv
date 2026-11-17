from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QMessageBox,
)


class EmployeesView(QWidget):
    def __init__(self, services=None, session=None):
        super().__init__()

        self.setWindowTitle("Employee Management")

        layout = QVBoxLayout(self)

        title = QLabel("Employee Management")
        title.setStyleSheet(
            "font-size:18px;"
            "font-weight:bold;"
            "padding:10px;"
        )

        layout.addWidget(title)

        form = QFormLayout()

        self.employee_id = QLineEdit()
        self.full_name = QLineEdit()
        self.cnic = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.department = QLineEdit()
        self.designation = QLineEdit()
        self.salary = QLineEdit()
        self.status = QLineEdit()

        form.addRow("Employee ID", self.employee_id)
        form.addRow("Full Name", self.full_name)
        form.addRow("CNIC", self.cnic)
        form.addRow("Phone", self.phone)
        form.addRow("Email", self.email)
        form.addRow("Department", self.department)
        form.addRow("Designation", self.designation)
        form.addRow("Salary", self.salary)
        form.addRow("Status", self.status)

        layout.addLayout(form)

        save_button = QPushButton("Save Employee")
        save_button.clicked.connect(self.save_employee)

        layout.addWidget(save_button)

    def save_employee(self):
        QMessageBox.information(
            self,
            "Employee",
            "Employee saved successfully."
        )

    def refresh(self):
        pass
    