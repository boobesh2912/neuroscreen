"""Authentication routes."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.security import get_current_user
from app.schemas.auth import LoginResponse, RegisterResponse, UserRegister, VerifyResponse
from app.services.auth_service import auth_service


router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(user: UserRegister):
    try:
        return auth_service.register_user(user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
):
    username = ""
    password = ""
    content_type = request.headers.get("content-type", "").lower()
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        username = str(form.get("username", "")).strip()
        password = str(form.get("password", ""))
    else:
        try:
            payload = await request.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON body") from exc
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    token = auth_service.authenticate_user(username, password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return token


@router.get("/verify", response_model=VerifyResponse)
async def verify_token(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}
