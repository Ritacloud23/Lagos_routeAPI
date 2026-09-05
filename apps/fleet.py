"""
fleet.py — GET /fleet/{bus_type}.

Attaches straight onto the shared `app` instance imported from main.py.
bus_type is typed as the BusType enum from model.py, so FastAPI both
rejects anything outside {brt, danfo, keke} with a 422 and renders it
as a dropdown on /docs.
"""

from main import app
from apps import data
from apps.model import BusResponse, BusType


@app.get("/fleet/{bus_type}", response_model=list[BusResponse], tags=["fleet"])
def get_fleet(bus_type: BusType) -> list[BusResponse]:
    buses = data.get_buses_by_type(bus_type.value)
    return [BusResponse(**bus) for bus in buses]
