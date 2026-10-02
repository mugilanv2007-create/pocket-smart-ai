from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class HomePlannerInput(BaseModel):
    total_budget: float = Field(..., gt=0)
    rooms: str = Field(..., min_length=2)
    required_items: str = Field(..., min_length=2)
    interior_style: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)
    priorities: str = Field(..., min_length=2)


class PartyPlannerInput(BaseModel):
    total_budget: float = Field(..., gt=0)
    guests: int = Field(..., gt=0)
    event_type: str = Field(..., min_length=2)
    venue: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)
    food_preference: str = Field(..., min_length=2)
    priorities: str = Field(..., min_length=2)


class JewelryPlannerInput(BaseModel):
    budget: float = Field(..., gt=0)
    occasion: str = Field(..., min_length=2)
    jewelry_style: str = Field(..., min_length=2)
    metal_preference: str = Field(..., min_length=2)
    outfit_description: str = Field(..., min_length=2)
    outfit_image_url: Optional[str] = None


class TripPlannerInput(BaseModel):
    total_budget: float = Field(..., gt=0)
    destination: str = Field(..., min_length=2)
    trip_type: str = Field(..., min_length=2)
    travelers: int = Field(..., gt=0)
    days: int = Field(..., gt=0)
    season: str = Field(..., min_length=2)
    travel_style: str = Field(..., min_length=2)
    preferences: str = Field(..., min_length=2)


class RecommendationDetailRequest(BaseModel):
    recommendation_id: int


class RecommendationResponse(BaseModel):
    summary: str
    budget_allocation: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    tips: List[str]


class TokenRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
