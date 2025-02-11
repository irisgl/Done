import logging
import os

def setup_logger(name, log_file='application.log', level=logging.INFO):
    """Create and configure a logger with specified name and log file."""
    
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Ensure no duplicate handlers
    if not logger.hasHandlers():
        # Create handlers
        log_folder = os.path.dirname(log_file)
        if log_folder and not os.path.exists(log_folder):
            os.makedirs(log_folder)
            
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()

        # Set log format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
