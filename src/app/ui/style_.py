from PySide6.QtWidgets import QApplication

QSS = """
* { font-family: "Segoe UI", sans-serif; font-size: 10pt; }
QWidget#nav-panel { background: #12263f; }
QLabel#brand { color: #ffffff; font-size: 13pt; font-weight: 600; padding: 16px 14px 4px 14px; }
QLabel#whoami { color: #9fb3c8; padding: 0 14px 12px 14px; }
QListWidget#nav { background: #12263f; border: none; color: #d9e2ec; outline: 0; }
QListWidget#nav::item { padding: 10px 14px; }
QListWidget#nav::item:selected { background: #1f3b5c; color: #ffffff; border-left: 3px solid #f08a24; }
QPushButton { background: #ffffff; border: 1px solid #c4ccd4; border-radius: 4px; padding: 6px 14px; }
QPushButton:hover { background: #eef3f8; }
QPushButton:disabled { color: #9aa5b1; background: #f4f6f8; }
QPushButton#primary { background: #2f6fed; color: #ffffff; border: 1px solid #2f6fed; }
QPushButton#primary:disabled { background: #a9c0f5; border-color: #a9c0f5; }
QPushButton#logout { margin: 12px; }
QTableWidget { gridline-color: #e3e8ee; selection-background-color: #dbe7fd; selection-color: #12263f; }
QHeaderView::section { background: #f0f3f7; padding: 6px; border: none; border-bottom: 1px solid #c4ccd4; font-weight: 600; }
QLabel#error { color: #c0362c; }
QLabel#title { font-size: 16pt; font-weight: 600; color: #12263f; }
QLabel#ok { color: #1b7f3b; font-weight: 600; }
QLabel#bad { color: #c0362c; font-weight: 600; }
"""


def apply_style(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(QSS)
