"""SDK decorators for agent definitions."""

import functools
import asyncio
import inspect
from typing import Any, Callable, Dict, Optional


def task(name: Optional[str] = None, retries: int = 0, timeout: int = 300):
    """Decorator for marking a method as an agent task handler."""
    if not isinstance(retries, int):
        raise TypeError("Retries must be an integer")
    if retries < 0:
        raise ValueError("Retries must be a non-negative integer")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValueError("Timeout must be a positive number")

    def decorator(func: Callable) -> Callable:
        is_coro = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if is_coro:
                try:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout,
                    )
                    return result
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Task {name or func.__name__} timed out after {timeout}s")
            else:
                loop = asyncio.get_running_loop()
                try:
                    partial_func = functools.partial(func, *args, **kwargs)
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, partial_func),
                        timeout=timeout,
                    )
                    return result
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Task {name or func.__name__} timed out after {timeout}s")

        # Preserve task metadata on the returned wrapper
        wrapper.__task_config__ = {
            "name": name or func.__name__,
            "retries": retries,
            "timeout": timeout,
        }
        return wrapper
    return decorator


def agent(name: str, version: str = "1.0.0", description: str = ""):
    """Decorator for marking a class as an agent definition."""
    def decorator(cls: type) -> type:
        cls.__agent_config__ = {
            "name": name,
            "version": version,
            "description": description,
        }
        return cls
    return decorator


def on_event(event_type: str):
    """Decorator for marking a method as an event handler."""
    def decorator(func: Callable) -> Callable:
        func.__event_handler__ = event_type

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper
    return decorator
