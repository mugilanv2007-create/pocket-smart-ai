from urllib.parse import quote_plus


SEARCH_PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k={query}",
    "Flipkart": "https://www.flipkart.com/search?q={query}",
    "IKEA India": "https://www.ikea.com/in/en/search/products/?q={query}",
    "Swiggy": "https://www.swiggy.com/search?query={query}",
    "Zomato": "https://www.zomato.com/search?query={query}",
    "OYO": "https://www.oyorooms.com/search?location=&query={query}",
    "Booking.com": "https://www.booking.com/searchresults.html?ss={query}",
    "Tripadvisor": "https://www.tripadvisor.com/Search?q={query}",
}


def build_search_link(platform: str, query: str) -> str:
    encoded = quote_plus(query)
    template = SEARCH_PLATFORMS.get(platform, "https://www.google.com/search?q={query}")
    return template.format(query=encoded)


def build_search_links(query: str) -> dict[str, str]:
    return {platform: build_search_link(platform, query) for platform in SEARCH_PLATFORMS}


def safe_budget_split(total_budget: float, percentages: list[tuple[str, float]]) -> list[dict]:
    items = []
    total = 0.0
    for category, percentage in percentages:
        amount = round(float(total_budget) * (float(percentage) / 100), 2)
        total += amount
        items.append({"category": category, "amount": amount, "percentage": int(round(percentage))})
    diff = round(float(total_budget) - total, 2)
    if items:
        items[-1]["amount"] = round(items[-1]["amount"] + diff, 2)
    return items
