from fastapi import APIRouter, HTTPException, Request

from app.auth import require_auth
from app.database import get_recommendation_by_id, get_recommendations_for_user, get_user_by_id
from app.models.schemas import (
    HomePlannerInput,
    JewelryPlannerInput,
    PartyPlannerInput,
    RecommendationDetailRequest,
    TripPlannerInput,
)
from app.services.recommendation_service import generate_recommendation

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "PocketSmart AI"}


@router.get("/session-info")
def session_info(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return {"authenticated": False, "user": None}
    try:
        user = get_user_by_id(int(user_id))
    except ValueError:
        return {"authenticated": False, "user": None}
    if not user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}


@router.get("/session-data")
def session_data(request: Request):
    return session_info(request)


@router.post("/generate-home")
def generate_home(payload: HomePlannerInput, request: Request):
    user_id = require_auth(request)
    response = generate_recommendation("home", payload.model_dump(), user_id=user_id)
    return response


@router.post("/generate-party")
def generate_party(payload: PartyPlannerInput, request: Request):
    user_id = require_auth(request)
    response = generate_recommendation("party", payload.model_dump(), user_id=user_id)
    return response


@router.post("/generate-jewelry")
def generate_jewelry(payload: JewelryPlannerInput, request: Request):
    user_id = require_auth(request)
    response = generate_recommendation("jewelry", payload.model_dump(), user_id=user_id)
    return response


@router.post("/generate-trip")
def generate_trip(payload: TripPlannerInput, request: Request):
    user_id = require_auth(request)
    response = generate_recommendation("trip", payload.model_dump(), user_id=user_id)
    return response


@router.post("/recommendations-details")
def recommendation_details(payload: RecommendationDetailRequest, request: Request):
    user_id = require_auth(request)
    recommendation = get_recommendation_by_id(int(payload.recommendation_id), user_id=user_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation


@router.get("/history-data")
def history_data(request: Request):
    user_id = require_auth(request)
    return {"items": get_recommendations_for_user(user_id)}
