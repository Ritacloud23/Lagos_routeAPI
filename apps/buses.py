"""
buses.py — GET /buses and GET /buses/{plate}.

Attaches straight onto the shared `app` instance imported from main.py.
Reuses the Plate doorway type from model.py rather than redeclaring
the plate regex here.
"""

from fastapi import HTTPException

from main import app
from apps import data
from apps.model import BusResponse, Plate


# A plain GET with no path or query parameters — there's nothing to
# validate at the doorway here, so it's just the full fleet.
@app.get("/buses", response_model=list[BusResponse], tags=["buses"])
def list_buses() -> list[BusResponse]:
    buses = data.get_all_buses()
    return [BusResponse(**bus) for bus in buses]


@app.get("/buses/{plate}", response_model=BusResponse, tags=["buses"])
def get_bus(plate: Plate) -> BusResponse:
    bus = data.get_bus_by_plate(plate)
    if bus is None:
        raise HTTPException(status_code=404, detail=f"No bus found with plate {plate}.")
    return BusResponse(**bus)
