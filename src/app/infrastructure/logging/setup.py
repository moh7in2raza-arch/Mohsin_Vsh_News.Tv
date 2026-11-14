import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging() -> Path:
    folder = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ERPOffice" / "logs"
    folder.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        folder / "erp.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    return folder