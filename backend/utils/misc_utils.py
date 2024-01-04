import time
from typing import Any, Callable, Tuple, Dict
from functools import wraps

from utils import logger


def time_execution(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to measure the execution time of a function and log the result.

    Parameters:
        func (Callable): The function to be executed and timed.

    Returns:
        Callable: The decorated function.
    """
    @wraps(func)
    def wrapper(*args: Tuple, **kwargs: Dict) -> Any:
        t1: float = time.time()
        result = func(*args, **kwargs)
        t2: float = time.time()

        formatted_args = ', '.join([repr(arg) for arg in args] + [f'{key}={repr(value)}' for key, value in kwargs.items()])
        logger.debug(f"`{func.__name__}({formatted_args})` was executed in {t2 - t1:.6f} seconds.")

        return result

    return wrapper
