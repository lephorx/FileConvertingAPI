import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name: str = "fileconverter", level: str = "INFO") -> logging.Logger:
    """Configure a rotating logger that writes to file and console."""
    log_file = os.path.join(LOG_DIR, "app.log")

    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    if not logger.handlers:
        file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
