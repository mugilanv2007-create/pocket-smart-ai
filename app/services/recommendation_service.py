from typing import Any

from app.database import save_recommendation
from app.services.gemini_service import generate_budget_plan


def generate_recommendation(planner: str, payload: dict[str, Any], user_id: int | None = None) -> dict[str, Any]:
    result = generate_budget_plan(planner, payload)
    cleaned = {
        "summary": str(result.get("summary") or "Smart recommendation plan."),
        "budget_allocation": result.get("budget_allocation") or [],
        "recommendations": result.get("recommendations") or [],
        "tips": result.get("tips") or [],
    }
    if user_id is not None:
        save_recommendation(user_id, planner, payload, cleaned)
    return cleaned
