"""
Logging configuration for ProdAssist
"""
import logging
import os
from datetime import datetime
from typing import Optional
from config.settings import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    app_name: Optional[str] = None
):
    """Setup application logging"""
    
    # Use settings defaults if not provided
    log_level = log_level or settings.log_level
    log_file = log_file or settings.log_file
    app_name = app_name or settings.app_name
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Create logger for the application
    logger = logging.getLogger(app_name)
    logger.info(f"🚀 {app_name} logging initialized - Level: {log_level}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


# Initialize default logger
app_logger = setup_logging()
