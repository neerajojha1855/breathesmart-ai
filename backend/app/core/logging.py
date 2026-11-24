import logging
import re
import sys

from app.core.config import settings

SENSITIVE_PATTERNS = [
    re.compile(r"password=([^\s&]+)", re.IGNORECASE),
    re.compile(r"bearer\s+([a-zA-Z0-9_\-\.]+)", re.IGNORECASE),
    re.compile(r"gsk_[a-zA-Z0-9]+", re.IGNORECASE),  # Groq API keys
    re.compile(r"npg_[a-zA-Z0-9]+", re.IGNORECASE),  # Neon passwords
]


class SanitizeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for pattern in SENSITIVE_PATTERNS:
            msg = pattern.sub("[REDACTED]", msg)
        return msg


def setup_logging() -> None:
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        SanitizeFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
