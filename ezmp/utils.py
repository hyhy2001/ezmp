import logging
from typing import Any

# Configure a basic, clean logger for the user
logger = logging.getLogger("ezmp")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s [ezmp]: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

class ErrorResult:
    """
    A simple wrapper class returned when a subprocess/thread throws an exception.
    This prevents the entire pool from crashing and allows the user to inspect failures.
    """
    def __init__(self, item: Any, exception: Exception):
        self.item = item
        self.exception = exception
        self.error_msg = str(exception)
        
    def __repr__(self):
        return f"<ErrorResult: {self.error_msg} on item {self.item}>"

def log_error(item: Any, exception: Exception) -> ErrorResult:
    """
    Logs an error and returns an ErrorResult object.
    """
    logger.error(f"Task failed for item: {item}. Error: {exception}")
    return ErrorResult(item, exception)
