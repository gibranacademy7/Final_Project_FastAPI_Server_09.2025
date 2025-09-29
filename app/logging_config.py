import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / "server.log"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("app")
