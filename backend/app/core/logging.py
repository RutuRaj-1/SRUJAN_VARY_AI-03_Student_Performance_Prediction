import logging
import sys
from app.core.config import get_settings

settings = get_settings()


def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
    )
    
    # Silence overly verbose third-party loggers in dev
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger = logging.getLogger("mastery")
    logger.info("Logging configured successfully at level %s", settings.LOG_LEVEL)
    return logger


logger = logging.getLogger("mastery")
