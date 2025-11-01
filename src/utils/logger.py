"""
Logging utilities for NextAstroTarget application.
Provides centralized logging configuration and setup.
"""

import logging
import logging.handlers
import os
from pathlib import Path
import configparser


def setup_logging(config_path: str = "config/config.ini"):
    """
    Set up logging configuration for the application.
    
    Args:
        config_path: Path to the configuration file
    """
    # Default values
    log_level = "INFO"
    log_file = "logs/nextastrotarget.log"
    max_log_size = "10MB"
    backup_count = 5
    
    # Read config if available
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        
        log_level = config.get('Logging', 'log_level', fallback=log_level)
        log_file = config.get('Logging', 'log_file', fallback=log_file)
        max_log_size = config.get('Logging', 'max_log_size', fallback=max_log_size)
        backup_count = config.getint('Logging', 'backup_count', fallback=backup_count)
    except Exception:
        # Use defaults if config reading fails
        pass
    
    # Ensure logs directory exists
    Path(os.path.dirname(log_file)).mkdir(parents=True, exist_ok=True)
    
    # Convert max_log_size to bytes
    max_bytes = _parse_size(max_log_size)
    
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Log the setup
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")


def _parse_size(size_str: str) -> int:
    """Parse size string like '10MB' into bytes."""
    size_str = size_str.upper().strip()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # Assume bytes
        return int(size_str)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module/logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class that provides logging functionality to other classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__module__)
        return self._logger


if __name__ == "__main__":
    # Test logging setup
    setup_logging()
    
    logger = get_logger(__name__)
    logger.info("This is a test info message")
    logger.warning("This is a test warning message")
    logger.error("This is a test error message")
    
    print("Logging test completed. Check logs/nextastrotarget.log")