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

    Example:

        @time_execution
        def some_func(*args, **keargs):
            pass
    """
    @wraps(func)
    def wrapper(*args: Tuple, **kwargs: Dict) -> Any:
        timestamp_01: float = time.time()
        result = func(*args, **kwargs)
        timestamp_02: float = time.time()

        formatted_args = ', '.join(
            [repr(arg) for arg in args] + [f'{key}={repr(value)}' for key, value in kwargs.items()])
        logger.debug(
            f"`{func.__name__}({formatted_args})` was executed in {timestamp_02 - timestamp_01:.6f} seconds.")

        return result

    return wrapper
