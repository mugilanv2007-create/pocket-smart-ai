from datetime import datetime

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import create_access_token, get_password_hash, get_current_user_id, verify_password
from app.database import create_user, get_user_by_email

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    email_clean = email.strip().lower()
    if not name.strip() or len(password) < 6:
        raise HTTPException(status_code=400, detail="Name is required and password must be at least 6 characters.")

    if get_user_by_email(email_clean):
        raise HTTPException(status_code=400, detail="Email is already registered.")

    create_user(name.strip(), email_clean, get_password_hash(password))
    return RedirectResponse(url="/login?registered=1", status_code=303)


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    email_clean = email.strip().lower()
    user = get_user_by_email(email_clean)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    response.set_cookie(key="user_id", value=str(user["id"]), httponly=False, samesite="lax")
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="user_id")
    return response


@router.post("/token")
async def token_login(payload: dict):
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}
