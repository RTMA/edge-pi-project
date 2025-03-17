# scripts/logger_setup.py

import logging
from logging.handlers import TimedRotatingFileHandler
import os

def setup_logger(log_dir="logs", log_filename="detectie.log"):
    logger = logging.getLogger("detectie_logger")

    if not logger.hasHandlers():
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_filename)

        logger.setLevel(logging.INFO)

        # Bestand handler
        file_handler = TimedRotatingFileHandler(log_path, when="D", interval=1, backupCount=30)
        file_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s | %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger
