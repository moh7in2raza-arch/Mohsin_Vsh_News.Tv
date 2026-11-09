import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

def main() -> int:
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("ERP Office Management")
    win.setCentralWidget(QLabel("Environment OK"))
    win.resize(480, 240)
    win.show()
    return app.exec()
