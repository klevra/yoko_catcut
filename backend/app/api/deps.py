from fastapi import Header, HTTPException, Query

from app.services.auth_service import AuthService

auth_service = AuthService()


def current_user(
    authorization: str = Header(default=""),
    token: str = Query(default=""),
) -> str:
    raw_token = token
    if authorization.lower().startswith("bearer "):
        raw_token = authorization.split(" ", 1)[1]
    try:
        return auth_service.authenticate(raw_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
