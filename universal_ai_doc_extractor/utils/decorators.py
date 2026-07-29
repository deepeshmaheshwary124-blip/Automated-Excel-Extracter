"""Utility decorators for thread safety, logging, and error handling."""

import functools
import logging
import threading
import time
from typing import Any, Callable, Optional

from models.enums import LogCategory
from database.repositories import ActivityLogRepository


logger = logging.getLogger(__name__)


def log_action(category: str = LogCategory.SYSTEM.value):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = int((time.time() - start) * 1000)
                repo = ActivityLogRepository()
                repo.log(func.__name__, category, "Success", elapsed, "success")
                return result
            except Exception as e:
                elapsed = int((time.time() - start) * 1000)
                repo = ActivityLogRepository()
                repo.log(func.__name__, category, str(e), elapsed, "error")
                raise

        return wrapper

    return decorator


def run_in_thread(widget: Any):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> threading.Thread:
            thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
            thread.start()
            return thread

        return wrapper

    return decorator


def ui_thread(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from PySide6.QtCore import QMetaObject, Qt
        from PySide6.QtWidgets import QWidget

        instance = args[0] if args else None
        if isinstance(instance, QWidget) and threading.current_thread() != threading.main_thread():
            QMetaObject.invokeMethod(
                instance, func.__name__, Qt.QueuedConnection
            )
            return None
        return func(*args, **kwargs)

    return wrapper


def safe_execute(default_return: Any = None):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error("Error in %s: %s", func.__name__, e, exc_info=True)
                return default_return

        return wrapper

    return decorator
