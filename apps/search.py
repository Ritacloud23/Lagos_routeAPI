"""
search.py — GET /search, and the bonus ?sort=fare.

Attaches straight onto the shared `app` instance imported from main.py.
"""

from typing import Literal, Optional

from fastapi import Query

from main import app
from apps import data
from apps.model import SearchResponse, SearchResultItem


@app.get("/search", response_model=SearchResponse, tags=["search"])
def search_routes(
    destination: str = Query(
        ...,
        min_length=3,
        max_length=30,
        description="Place name to search for among each route's stops.",
    ),
    max_fare: Optional[float] = Query(
        None,
        gt=0,
        description="Keep only routes at or under this fare.",
    ),
    sort: Optional[Literal["fare"]] = Query(
        None,
        description="Bonus: sort results by fare, ascending.",
    ),
) -> SearchResponse:
    routes = data.get_all_routes()

    matches: list[dict] = [
        route
        for route in routes
        if any(destination.lower() in stop.lower() for stop in route["stops"])
    ]

    if max_fare is not None:
        matches = [route for route in matches if route["fare_naira"] <= max_fare]

    if sort == "fare":
        matches = sorted(matches, key=lambda route: route["fare_naira"])

    return SearchResponse(
        destination=destination,
        max_fare=max_fare,
        sort=sort,
        results=[SearchResultItem(**route) for route in matches],
    )
