import logging

def setup_logger(log_file="app.log"):
    """Setup logger to record app actions."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Log to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_action(message):
    """Log a custom action."""
    logging.info(message)
