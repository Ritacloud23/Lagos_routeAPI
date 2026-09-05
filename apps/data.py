"""
data.py — the office. Loads lagos_routes.json once, at startup, and
keeps it in memory. Nothing here knows about HTTP; it just answers
plain-Python questions about routes and buses.
"""

import json
from pathlib import Path
from typing import Any, Optional

DATA_FILE: Path = Path(__file__).resolve().parent.parent / "lagos_routes.json"

_routes: list[dict[str, Any]] = []
_buses: list[dict[str, Any]] = []
_loaded: bool = False


def load_data() -> None:
    """Read lagos_routes.json from disk exactly once and cache it in memory."""
    global _routes, _buses, _loaded

    if _loaded:
        return

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        raw_data: dict[str, Any] = json.load(file)

    _routes = [
        {**route, "number": route["route_number"]}
        for route in raw_data.get("routes", [])
    ]
    _buses = [
        {**bus, "type": bus["bus_type"]}
        for bus in raw_data.get("buses", [])
    ]
    _loaded = True


def get_all_routes() -> list[dict[str, Any]]:
    return _routes


def get_all_buses() -> list[dict[str, Any]]:
    return _buses


def get_route_by_number(route_number: int) -> Optional[dict[str, Any]]:
    for route in _routes:
        if route["number"] == route_number:
            return route
    return None


def get_bus_by_plate(plate: str) -> Optional[dict[str, Any]]:
    for bus in _buses:
        if bus["plate"] == plate:
            return bus
    return None


def get_buses_by_type(bus_type: str) -> list[dict[str, Any]]:
    return [bus for bus in _buses if bus["type"] == bus_type]


def get_buses_by_route(route_number: int) -> list[dict[str, Any]]:
    return [bus for bus in _buses if bus["route_number"] == route_number]
