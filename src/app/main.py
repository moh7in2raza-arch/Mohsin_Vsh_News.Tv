import logging
import sys

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QMessageBox

from src.app.bootstrap import build_services, start_logging
from src.app.ui.login_window import LoginWindow
from src.app.ui.main_window import VshNewsMainWindow
from src.app.ui.style import apply_style

log = logging.getLogger(__name__)


class Shell:
    """Owns the top-level windows: login <-> main."""

    def __init__(self, services):
        self._services = services
        self._main = None

        self.login = LoginWindow(services.auth)
        self.login.authenticated.connect(self._open_main)

    def start(self) -> None:
        if self._main is not None:
            self._main.hide()

        self.login.reset()
        self.login.show()
        self.login.raise_()
        self.login.activateWindow()

    def _open_main(self, session) -> None:
        self._main = VshNewsMainWindow(
            self._services,
            session
        )

        self._main.logged_out.connect(self.start)

        self._main.show()
        self.login.hide()

    def shutdown(self) -> None:
        main, self._main = self._main, None

        if main is not None:
            main.shutdown()
            main.deleteLater()

        self.login.close()
        self.login.deleteLater()

        app = QApplication.instance()

        if app is not None:
            QCoreApplication.sendPostedEvents(
                None,
                QEvent.Type.DeferredDelete,
            )
            app.processEvents()


def _excepthook(exc_type, exc, tb) -> None:
    log.critical(
        "Unhandled error",
        exc_info=(exc_type, exc, tb),
    )

    QMessageBox.critical(
        None,
        "Unexpected error",
        f"{exc_type.__name__}: {exc}",
    )


def main() -> int:
    start_logging()

    sys.excepthook = _excepthook

    app = QApplication(sys.argv)

    apply_style(app)

    services = build_services()

    shell = Shell(services)

    shell.start()

    try:
        return app.exec()
    finally:
        shell.shutdown()


if __name__ == "__main__":
    sys.exit(main())
    