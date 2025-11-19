import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    max_bytes: int = 10_485_760,
    backup_count: int = 5
):
    """
    Configure centralized logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files. If None, uses './logs'
        enable_file_logging: Whether to log to files
        enable_console_logging: Whether to log to console
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    detailed_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    root_logger.handlers.clear()
    
    if enable_console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
    
    if enable_file_logging:
        app_log_file = os.path.join(log_dir, "app.log")
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        app_handler.setLevel(numeric_level)
        app_handler.setFormatter(detailed_format)
        root_logger.addHandler(app_handler)
        
        error_log_file = os.path.join(log_dir, "error.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_format)
        root_logger.addHandler(error_handler)
    
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured - Level: {log_level}, Directory: {log_dir}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
