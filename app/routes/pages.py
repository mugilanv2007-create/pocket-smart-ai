from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import require_auth
from app.database import get_user_by_id

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _current_user(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    try:
        return get_user_by_id(int(user_id))
    except (TypeError, ValueError):
        return None


@router.get("/")
async def index(request: Request):
    user = _current_user(request)
    return templates.TemplateResponse(request, "index.html", {"user": user})


@router.get("/register")
async def register_page(request: Request):
    user = _current_user(request)
    return templates.TemplateResponse(request, "register.html", {"user": user})


@router.get("/login")
async def login_page(request: Request):
    user = _current_user(request)
    return templates.TemplateResponse(request, "login.html", {"user": user})


@router.get("/dashboard")
async def dashboard(request: Request):
    try:
        user_id = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    user = get_user_by_id(user_id)
    return templates.TemplateResponse(request, "dashboard.html", {"user": user})


@router.get("/history")
async def history(request: Request):
    try:
        user_id = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    user = get_user_by_id(user_id)
    return templates.TemplateResponse(request, "history.html", {"user": user})


@router.get("/planner/home")
async def home_planner(request: Request):
    try:
        user_id = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    user = get_user_by_id(user_id)
    return templates.TemplateResponse(request, "home_planner.html", {"user": user})


@router.get("/planner/party")
async def party_planner(request: Request):
    try:
        user_id = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    user = get_user_by_id(user_id)
    return templates.TemplateResponse(request, "party_planner.html", {"user": user})


@router.get("/planner/jewelry")
async def jewelry_planner(request: Request):
    try:
        user_id = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    user = get_user_by_id(user_id)
    return templates.TemplateResponse(request, "jewelry_planner.html", {"user": user})


@router.get("/planner/trip")
async def trip_planner(request: Request):
    try:
        user_id = require_auth(request)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    user = get_user_by_id(user_id)
    return templates.TemplateResponse(request, "trip_planner.html", {"user": user})
