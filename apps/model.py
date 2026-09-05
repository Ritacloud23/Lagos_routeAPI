"""
model.py — the shapes, and the reusable doorway types.

Response models, the BusType enum, and a set of Annotated type aliases
(RouteNumber, Plate) that carry their validation rule with them. Any
endpoint that needs "a route number" or "a plate" imports the type
from here instead of re-declaring the Path() constraint by hand — this
is how the same doorway rule gets reused across every route that needs
it, without being copied.
"""

from enum import Enum
from typing import Annotated, Optional

from fastapi import Path
from pydantic import BaseModel


class BusType(str, Enum):
    """The union runs exactly three kinds of bus. Nothing else is valid.

    Because this is a str Enum used as a path-parameter type, FastAPI
    renders it as a dropdown on /docs and rejects anything outside
    these three values with a 422 before the function body ever runs.
    """
    brt = "brt"
    danfo = "danfo"
    keke = "keke"


# ---------------------------------------------------------------------------
# Reusable doorway types — declared once, imported everywhere they're needed.
# ---------------------------------------------------------------------------
RouteNumber = Annotated[
    int,
    Path(..., ge=1, le=200, description="Route numbers in Lagos run from 1 to 200."),
]

Plate = Annotated[
    str,
    Path(
        ...,
        pattern=r"^[A-Z]{3}-\d{3}[A-Z]{2}$",
        description=(
            "Lagos plate shape: three capital letters, a dash, three digits, "
            "two capital letters, e.g. LSD-441KJ."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------
class WelcomeResponse(BaseModel):
    message: str
    total_routes: int
    total_buses: int


class RouteResponse(BaseModel):
    number: int
    name: str
    start: str
    end: str
    fare_naira: float
    stops: list[str]


class RouteStopsResponse(BaseModel):
    route_number: int
    stops: list[str]
    skip: int
    limit: int
    total_stops: int


class BusResponse(BaseModel):
    plate: str
    type: BusType
    route_number: int


class SearchResultItem(BaseModel):
    number: int
    name: str
    start: str
    end: str
    fare_naira: float
    stops: list[str]


class SearchResponse(BaseModel):
    destination: str
    max_fare: Optional[float] = None
    sort: Optional[str] = None
    results: list[SearchResultItem]
