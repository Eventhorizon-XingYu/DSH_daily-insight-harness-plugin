"""Shared utility functions for retries, logging, and safe slugs."""
from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])
def setup_logging() -> None:
    """Configure concise application logging."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
def slugify(value: str) -> str:
    """Convert a topic into a filesystem-safe lowercase slug."""
    value = value.lower().strip().replace(" ", "-")
    value = re.sub(r"[^a-z0-9\-]+", "", value)
    return re.sub(r"-+", "-", value).strip("-") or "topic"
def retry(attempts: int = 3, delay: float = 0.5) -> Callable[[F], F]:
    """Retry a function after exceptions, preserving its final error."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            error: Exception | None = None
            for index in range(attempts):
                try: return func(*args, **kwargs)
                except Exception as exc:
                    error = exc
                    if index + 1 < attempts: time.sleep(delay)
            assert error is not None
            raise error
        return wrapper  # type: ignore[return-value]
    return decorator
