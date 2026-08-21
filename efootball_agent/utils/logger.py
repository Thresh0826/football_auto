from __future__ import annotations

import logging
from pathlib import Path


def get_logger() -> logging.Logger:
    logger = logging.getLogger("efootball_agent")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    Path("logs").mkdir(exist_ok=True)
    file_handler = logging.FileHandler("logs/agent.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

