import json
import re
from typing import Any

from google import genai

from app.config import settings
from app.services.catalog import build_search_links, safe_budget_split


def _extract_json_from_text(text: str) -> Any:
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def _build_default_response(planner: str, payload: dict[str, Any]) -> dict[str, Any]:
    total_budget = float(payload.get("total_budget") or payload.get("budget") or 0)
    guest_count = int(payload.get("guests") or 20)
    destination = payload.get("destination", "your destination")
    travelers = int(payload.get("travelers") or 2)
    days = int(payload.get("days") or 3)
    if planner == "home":
        allocation = safe_budget_split(total_budget, [("Furniture", 40), ("Lighting", 18), ("Decor", 22), ("Storage", 10), ("Accessories", 10)])
        recommendations = [
            {
                "name": "Modular Sofa Set",
                "category": "Furniture",
                "estimated_price": round(total_budget * 0.26, 2),
                "platform": "Amazon",
                "reason": "Space-efficient and suitable for compact Indian homes with a modern style.",
                "search_query": "modern modular sofa set for living room",
                "link": build_search_links("modern modular sofa set for living room")["Amazon"],
            },
            {
                "name": "Smart LED Ceiling Lights",
                "category": "Lighting",
                "estimated_price": round(total_budget * 0.12, 2),
                "platform": "Flipkart",
                "reason": "Enhances the room ambience while keeping the budget realistic.",
                "search_query": "smart led ceiling lights for home",
                "link": build_search_links("smart led ceiling lights for home")["Flipkart"],
            },
        ]
        tips = [
            "Prioritize functional pieces first, then add decorative accents.",
            "Choose durable materials that suit your local climate and usage.",
        ]
    elif planner == "party":
        guest_count = int(payload.get("guests") or 20)
        allocation = safe_budget_split(total_budget, [("Food & Drinks", 38), ("Venue & Rentals", 25), ("Decorations", 18), ("Entertainment", 12), ("Miscellaneous", 7)])
        recommendations = [
            {
                "name": "Buffet-style meal package",
                "category": "Food & Drinks",
                "estimated_price": round(total_budget * 0.24, 2),
                "platform": "Swiggy",
                "reason": "Cost-effective and convenient for larger guest groups.",
                "search_query": "party buffet catering for 20 guests",
                "link": build_search_links("party buffet catering for 20 guests")["Swiggy"],
            },
            {
                "name": "Budget-friendly venue setup",
                "category": "Venue & Rentals",
                "estimated_price": round(total_budget * 0.18, 2),
                "platform": "OYO",
                "reason": "Helps maintain an elegant look without overspending.",
                "search_query": "party venue rental near me",
                "link": build_search_links("party venue rental near me")["OYO"],
            },
        ]
        tips = [
            "Bundle décor and entertainment to reduce vendor coordination costs.",
            "Keep menu choices flexible so you can handle guest dietary preference changes.",
        ]
    elif planner == "trip":
        allocation = safe_budget_split(total_budget, [("Stay", 32), ("Food", 20), ("Transport", 18), ("Activities", 20), ("Contingency", 10)])
        recommendations = [
            {
                "name": f"Comfortable stay in {destination}",
                "category": "Stay",
                "estimated_price": round(total_budget * 0.24, 2),
                "platform": "Booking.com",
                "reason": "Balances cost and comfort for a short, value-driven trip.",
                "search_query": f"budget hotels in {destination} for {travelers} travelers",
                "link": build_search_links(f"budget hotels in {destination} for {travelers} travelers")["Booking.com"],
            },
            {
                "name": "Local food and sightseeing combo",
                "category": "Activities",
                "estimated_price": round(total_budget * 0.16, 2),
                "platform": "Tripadvisor",
                "reason": "Offers memorable local experiences while staying within budget.",
                "search_query": f"best local food and sightseeing in {destination}",
                "link": build_search_links(f"best local food and sightseeing in {destination}")["Tripadvisor"],
            },
        ]
        tips = [
            "Book transportation early and keep one flexible day for spontaneous local experiences.",
            "Choose one major activity each day and leave room for food and rest.",
        ]
    else:
        allocation = safe_budget_split(total_budget, [("Centerpiece Jewelry", 42), ("Earrings", 22), ("Bracelet", 16), ("Ring", 20)])
        recommendations = [
            {
                "name": "Minimal Gold Necklace Set",
                "category": "Centerpiece Jewelry",
                "estimated_price": round(total_budget * 0.28, 2),
                "platform": "Amazon",
                "reason": "Classic design that matches weddings and festive occasions with elegant styling.",
                "search_query": "gold necklace set for festive occasion",
                "link": build_search_links("gold necklace set for festive occasion")["Amazon"],
            },
            {
                "name": "Pearl and Diamond Earrings",
                "category": "Earrings",
                "estimated_price": round(total_budget * 0.17, 2),
                "platform": "Flipkart",
                "reason": "Adds balance to Indian bridal or festive outfits without exceeding the budget.",
                "search_query": "pearl diamond earrings for occasion",
                "link": build_search_links("pearl diamond earrings for occasion")["Flipkart"],
            },
        ]
        tips = [
            "Match metal and gemstone tones with your outfit to create a cohesive look.",
            "Keep the final set balanced: one statement piece and one accent item is enough.",
        ]

    summary = {
        "home": f"A styled home plan for {payload.get('rooms', 'your rooms')} with a balanced budget of ₹{int(total_budget):,}.",
        "party": f"An event plan for {guest_count} guests, keeping the spend practical and high-impact in {payload.get('location', 'your area')}.",
        "trip": f"A {payload.get('trip_type', 'travel')} plan for {travelers} travelers visiting {destination} for {days} days within a ₹{int(total_budget):,} budget.",
        "jewelry": f"A jewelry recommendation set for {payload.get('occasion', 'your event')} using a polished {payload.get('metal_preference', 'gold')} finish.",
    }.get(planner, f"Smart recommendation plan for your {planner} budget.")

    return {
        "summary": summary,
        "budget_allocation": allocation,
        "recommendations": recommendations,
        "tips": tips,
    }


def _normalize_response(payload: dict[str, Any], planner: str, request_payload: dict[str, Any]) -> dict[str, Any]:
    safe_payload = payload or {}
    recommendations = safe_payload.get("recommendations")
    if not isinstance(recommendations, list):
        recommendations = []

    budget_allocation = safe_payload.get("budget_allocation")
    if not isinstance(budget_allocation, list):
        budget_allocation = []

    normalized = {
        "summary": str(safe_payload.get("summary") or "Smart personal recommendation plan."),
        "budget_allocation": [
            {
                "category": str(item.get("category") or "General"),
                "amount": round(float(item.get("amount") or 0), 2),
                "percentage": int(item.get("percentage") or 0),
            }
            for item in budget_allocation
        ],
        "recommendations": [
            {
                "name": str(item.get("name") or "Recommended product"),
                "category": str(item.get("category") or "General"),
                "estimated_price": round(float(item.get("estimated_price") or 0), 2),
                "platform": str(item.get("platform") or "Amazon"),
                "reason": str(item.get("reason") or "Matches your preferences and budget."),
                "search_query": str(item.get("search_query") or "smart purchase"),
                "link": str(item.get("link") or "https://www.google.com/search?q=" + str(item.get("search_query") or "smart purchase")),
            }
            for item in recommendations
        ],
        "tips": [
            str(tip) for tip in (safe_payload.get("tips") or []) if str(tip).strip()
        ],
    }

    if not normalized["budget_allocation"]:
        total_budget = float(request_payload.get("total_budget") or request_payload.get("budget") or 0)
        normalized["budget_allocation"] = safe_budget_split(total_budget, [("Core Needs", 50), ("Comfort", 25), ("Style", 15), ("Contingency", 10)])
    if not normalized["recommendations"]:
        normalized["recommendations"] = [
            {
                "name": "Budget-friendly recommended option",
                "category": "General",
                "estimated_price": float(request_payload.get("total_budget") or request_payload.get("budget") or 0) * 0.35,
                "platform": "Amazon",
                "reason": "Practical option selected to balance style, utility, and budget fit.",
                "search_query": f"{planner} recommendation budget friendly",
                "link": "https://www.google.com/search?q=" + f"{planner} recommendation budget friendly",
            }
        ]
    if not normalized["tips"]:
        normalized["tips"] = [
            "Keep a small contingency reserve for last-minute changes.",
            "Compare estimated prices across trusted stores before buying.",
        ]
    return normalized


def generate_budget_plan(planner: str, payload: dict[str, Any]) -> dict[str, Any]:
    if settings.mock_mode or not settings.gemini_api_key:
        return _build_default_response(planner, payload)

    candidate_models = []
    if settings.gemini_model:
        candidate_models.append(settings.gemini_model)
    if settings.gemini_model != "gemini-2.0-flash":
        candidate_models.append("gemini-2.0-flash")
    candidate_models = list(dict.fromkeys(candidate_models))

    last_error: Exception | None = None
    for model_name in candidate_models:
        try:
            client = genai.Client(api_key=settings.gemini_api_key)
            prompt = (
                f"You are a smart budget planner for PocketSmart AI. "
                f"Planner: {planner}. "
                f"User inputs: {json.dumps(payload, ensure_ascii=False)}. "
                "Return valid JSON with exact keys: summary, budget_allocation, recommendations, tips. "
                "Use Indian Rupees, estimated prices, and practical purchase suggestions. "
                "Keep recommendations reasonably within the total budget. "
                "For jewelry, consider the outfit description or image cues if present. "
                "The response must be valid JSON only, no markdown fences."
            )
            response = client.models.generate_content(model=model_name, contents=prompt)
            text = getattr(response, "text", None)
            if text is None:
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                        text = "".join(part.text for part in candidate.content.parts if getattr(part, "text", None))
            if not text:
                raise ValueError("Gemini returned no content.")
            parsed = _extract_json_from_text(text)
            if not isinstance(parsed, dict):
                raise ValueError("Gemini output was not valid JSON.")
            return _normalize_response(parsed, planner, payload)
        except Exception as exc:  # pragma: no cover - fallback path for live API errors
            last_error = exc
    if last_error is not None:
        return _build_default_response(planner, payload)
    return _build_default_response(planner, payload)
