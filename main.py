"""
main.py — creates the one shared `app` instance and the welcome route.

Every other endpoint lives in its own file under apps/ (routes.py,
buses.py, fleet.py, search.py). Each of those files does
`from main import app` and decorates it directly with @app.get —
no APIRouter, no include_router. They're imported here, at the
bottom, only for their side effect of registering routes onto `app`.
That import must happen AFTER `app = FastAPI(...)` below, since each
module reaches back into this one for the same `app` object.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps import data
from apps.model import WelcomeResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    data.load_data()
    yield


app = FastAPI(
    title="Lagos Route Window",
    description="A read-only FastAPI service for Lagos routes and buses.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_model=WelcomeResponse, tags=["home"])
def home() -> WelcomeResponse:
    return WelcomeResponse(
        message="Welcome to the Lagos Route Window",
        total_routes=len(data.get_all_routes()),
        total_buses=len(data.get_all_buses()),
    )


# Registers /routes/*, /buses/*, /fleet/*, /search onto `app` above.
from apps import routes as _routes_endpoints  # noqa: E402,F401
from apps import buses as _buses_endpoints  # noqa: E402,F401
from apps import fleet as _fleet_endpoints  # noqa: E402,F401
from apps import search as _search_endpoints  # noqa: E402,F401
