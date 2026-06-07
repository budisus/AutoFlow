"""
Utility functions for AutoFlow.
"""

import logging
import json
from typing import Any, Dict
from datetime import datetime
from functools import wraps
import hashlib


def setup_logging(level: int = logging.INFO, format: str = None) -> None:
    """Configure logging for the application."""
    if format is None:
        format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    logging.basicConfig(
        level=level,
        format=format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry a function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    logging.warning(f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {current_delay}s")
                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


def hash_context(context: Dict[str, Any]) -> str:
    """Generate a hash of the workflow context."""
    normalized = json.dumps(context, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


class Logger:
    """Structured logger with context."""
    
    def __init__(self, name: str, workflow_id: str = None):
        self.logger = logging.getLogger(name)
        self.workflow_id = workflow_id or "unknown"
    
    def log(self, level: int, msg: str, **kwargs):
        extra = {"workflow_id": self.workflow_id, **kwargs}
        self.logger.log(level, msg, extra=extra)
    
    def info(self, msg: str, **kwargs):
        self.log(logging.INFO, msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        self.log(logging.ERROR, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        self.log(logging.WARNING, msg, **kwargs)