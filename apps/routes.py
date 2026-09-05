"""
routes.py — GET /routes/{route_number}, GET /routes/{route_number}/stops,
and the bonus GET /routes/{route_number}/buses.

Attaches straight onto the shared `app` instance imported from main.py.
No APIRouter here — each endpoint is a plain @app.get.
"""

from fastapi import HTTPException, Query

from main import app
from apps import data
from apps.model import BusResponse, RouteNumber, RouteResponse, RouteStopsResponse


@app.get("/routes/{route_number}", response_model=RouteResponse, tags=["routes"])
def get_route(route_number: RouteNumber) -> RouteResponse:
    route = data.get_route_by_number(route_number)
    if route is None:
        raise HTTPException(status_code=404, detail=f"No route found with number {route_number}.")
    return RouteResponse(**route)


@app.get("/routes/{route_number}/stops", response_model=RouteStopsResponse, tags=["routes"])
def get_route_stops(
    route_number: RouteNumber,
    limit: int = Query(5, ge=1, le=10, description="How many stops to show, 1 to 10."),
    skip: int = Query(0, ge=0, description="How many stops to skip from the start."),
) -> RouteStopsResponse:
    route = data.get_route_by_number(route_number)
    if route is None:
        raise HTTPException(status_code=404, detail=f"No route found with number {route_number}.")

    all_stops: list[str] = route["stops"]
    windowed_stops: list[str] = all_stops[skip: skip + limit]

    return RouteStopsResponse(
        route_number=route_number,
        stops=windowed_stops,
        skip=skip,
        limit=limit,
        total_stops=len(all_stops),
    )


# Bonus: reuses RouteNumber, the exact same doorway rule as get_route()
# above, without redeclaring ge=1, le=200 anywhere.
@app.get("/routes/{route_number}/buses", response_model=list[BusResponse], tags=["routes"])
def get_route_buses(route_number: RouteNumber) -> list[BusResponse]:
    route = data.get_route_by_number(route_number)
    if route is None:
        raise HTTPException(status_code=404, detail=f"No route found with number {route_number}.")

    buses = data.get_buses_by_route(route_number)
    return [BusResponse(**bus) for bus in buses]
