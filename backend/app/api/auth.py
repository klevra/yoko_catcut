from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


class LoginRequest(BaseModel):
    user_id: str
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    try:
        return auth_service.login(payload.user_id, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
