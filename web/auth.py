"""Authentication helpers — single shared password with signed cookie."""

import os
from functools import wraps

from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

COOKIE_NAME = "rand_session"
MAX_AGE = 8 * 3600  # 8 hours


def _get_serializer():
    secret = os.getenv("APP_SECRET_KEY", "change-me")
    return URLSafeTimedSerializer(secret)


def check_password(password: str) -> bool:
    expected = os.getenv("APP_PASSWORD", "rand2026")
    return password == expected


def set_session_cookie(response: Response) -> Response:
    s = _get_serializer()
    token = s.dumps({"authenticated": True})
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return response


def clear_session_cookie(response: Response) -> Response:
    response.delete_cookie(COOKIE_NAME)
    return response


def is_authenticated(request: Request) -> bool:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    s = _get_serializer()
    try:
        data = s.loads(token, max_age=MAX_AGE)
        return data.get("authenticated", False)
    except (BadSignature, SignatureExpired):
        return False


def require_auth(request: Request):
    """Return a RedirectResponse to login if not authenticated, else None."""
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return None
