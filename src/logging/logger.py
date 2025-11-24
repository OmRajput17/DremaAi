"""
Logging Configuration Module
Provides centralized logging setup with file rotation and console output
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class LoggerSetup:
    """Setup and configure application logging."""
    
    def __init__(self, app_name="drema_ai", log_dir="logs"):
        """
        Initialize logger setup.
        
        Args:
            app_name (str): Name of the application
            log_dir (str): Directory to store log files
        """
        self.app_name = app_name
        self.log_dir = log_dir
        self.log_file = f"{app_name}_{datetime.now().strftime('%Y%m%d')}.log"
        self.log_path = os.path.join(self.log_dir, self.log_file)
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
    
    def get_logger(self, name):
        """
        Get or create a logger with the specified name.
        
        Args:
            name (str): Logger name (usually __name__)
        
        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(name)
        
        # Only add handlers if they haven't been added yet
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            simple_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            
            # File handler with rotation (10MB max, keep 5 backups)
            file_handler = RotatingFileHandler(
                self.log_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            
            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger


# Global logger setup instance
_logger_setup = LoggerSetup()


def get_logger(name):
    """
    Convenience function to get a logger.
    
    Args:
        name (str): Logger name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return _logger_setup.get_logger(name)