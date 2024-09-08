from functools import wraps
from typing import Any, Awaitable, Callable

from fastapi import HTTPException, Request

from app.config import TOKEN


# Authentication decorator
def authenticator() -> (
    Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]
):
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args: Any, request: Request, **kwargs: Any):
            token: str = request.headers.get("Authorization", "")
            if not token or token != f"Bearer {TOKEN}":
                raise HTTPException(status_code=401, detail="Unauthorized")
            return await func(*args, request, **kwargs)

        return wrapper

    return decorator
