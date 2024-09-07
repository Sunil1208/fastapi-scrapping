from functools import wraps

from fastapi import HTTPException, Request

from app.config import TOKEN


# Authentication decorator
def authenticator():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            token = request.headers.get("Authorization")
            if not token or token != f"Bearer {TOKEN}":
                raise HTTPException(status_code=401, detail="Unauthorized")
            return await func(*args, request, **kwargs)

        return wrapper

    return decorator
