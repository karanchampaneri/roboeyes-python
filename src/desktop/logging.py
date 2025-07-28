"""
Logging system for RoboEyes Desktop application.

This module provides centralized logging functionality for debugging and error tracking
throughout the RoboEyes desktop application.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class RoboEyesLogger:
    """
    Centralized logging system for RoboEyes Desktop.
    
    This class provides structured logging with different levels and output options,
    including console output and file logging for debugging and error tracking.
    """
    
    def __init__(self, name: str = "RoboEyes", debug: bool = False, log_file: Optional[str] = None):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            debug: Enable debug level logging
            log_file: Optional path to log file
        """
        self.logger = logging.getLogger(name)
        self.debug_enabled = debug
        
        # Set logging level
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Create file handler if log file is specified
        if log_file:
            self._setup_file_logging(log_file)
    
    def _setup_file_logging(self, log_file: str) -> None:
        """
        Set up file logging.
        
        Args:
            log_file: Path to log file
        """
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            self.info(f"File logging enabled: {log_file}")
            
        except Exception as e:
            self.error(f"Failed to setup file logging: {e}")
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """Log exception with traceback."""
        self.logger.exception(message)


# Global logger instance
_global_logger: Optional[RoboEyesLogger] = None


def get_logger() -> RoboEyesLogger:
    """
    Get the global logger instance.
    
    Returns:
        Global RoboEyesLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = RoboEyesLogger()
    return _global_logger


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> RoboEyesLogger:
    """
    Set up the global logging system.
    
    Args:
        debug: Enable debug level logging
        log_file: Optional path to log file
        
    Returns:
        Configured RoboEyesLogger instance
    """
    global _global_logger
    _global_logger = RoboEyesLogger(debug=debug, log_file=log_file)
    return _global_logger


def get_default_log_file() -> str:
    """
    Get the default log file path.
    
    Returns:
        Default log file path
    """
    # Import here to avoid circular imports
    from .platform_compat import get_platform_compat
    
    # Use platform-appropriate log directory
    platform_compat = get_platform_compat()
    log_dir = platform_compat.get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(log_dir / f"roboeyes_{timestamp}.log")