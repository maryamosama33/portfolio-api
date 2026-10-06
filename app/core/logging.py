import logging

from app.core.config import settings

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def setup_logging() -> None:
    logging.basicConfig(level=settings.log_level.upper(), format=LOG_FORMAT)
    # Third-party clients are chatty at INFO.
    for noisy in ("httpx", "google_genai", "pymongo"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
