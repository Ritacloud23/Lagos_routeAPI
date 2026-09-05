# The Lagos Route Window

A read-only FastAPI service for the Lagos transport union. Answers questions
about routes and buses over HTTP — nothing here accepts a write. Every rule
is enforced **at the doorway**: FastAPI's own validation rejects a bad
request with a `422` before any of your function bodies ever run.

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

## Running it

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open **http://127.0.0.1:8000/docs** — the whole demo happens there.
Every constraint below (ranges, patterns, enums, defaults) is visible on
that page, not just enforced silently.

## Project structure

```
main.py           # Creates the shared `app`, lifespan, GET / — then
                   # imports the four files below so they can register
                   # their own routes on that same `app`.
apps/
  data.py         # The office: loads lagos_routes.json once at startup.
                   # Nothing here knows about HTTP.
  model.py        # The shapes: response models, the BusType enum, and
                   # the reusable doorway types RouteNumber and Plate.
  routes.py       # GET /routes/{route_number}
                   # GET /routes/{route_number}/stops
                   # GET /routes/{route_number}/buses   (bonus)
  buses.py        # GET /buses/{plate}
  fleet.py        # GET /fleet/{bus_type}
  search.py       # GET /search   (with the bonus ?sort=fare)
lagos_routes.json # The union's records: 28 routes, 60 buses.
requirements.txt
```

There is no `APIRouter` anywhere in this project. Each endpoint file
does `from main import app` and decorates that one shared instance
directly with `@app.get(...)`. `main.py` only imports those files
*after* `app` is created, since each of them reaches back into `main`
for it.

## Endpoints

| Method & path | What it answers |
|---|---|
| `GET /` | A welcome message, plus how many routes and buses the union runs. |
| `GET /routes/{route_number}` | Full details of one route. |
| `GET /routes/{route_number}/stops?limit=&skip=` | A paged window over that route's stops. |
| `GET /routes/{route_number}/buses` | Every bus serving that route. *(bonus)* |
| `GET /buses` | The whole fleet — no parameters, so nothing to validate at the doorway. |
| `GET /buses/{plate}` | Details of one bus by its plate. |
| `GET /fleet/{bus_type}` | All buses of one kind: `brt`, `danfo`, or `keke`. |
| `GET /search?destination=&max_fare=&sort=` | Every route passing through a place, optionally capped by fare and sorted. `sort=fare` is the *bonus*. |

## The doorway rules

Every rule below is declared, not hand-checked — a value that breaks one
never reaches a function body. FastAPI answers with `422` and a JSON
explanation automatically.

| Rule | Where it's declared |
|---|---|
| Route numbers must be 1–200 | `RouteNumber = Annotated[int, Path(..., ge=1, le=200)]` in `model.py` |
| Plates must match `AAA-999AA` | `Plate = Annotated[str, Path(..., pattern=r"^[A-Z]{3}-\d{3}[A-Z]{2}$")]` in `model.py` |
| Bus type must be one of three kinds | `BusType(str, Enum)` in `model.py` — also renders as a dropdown on `/docs` |
| `limit` (stops) must be 1–10, defaults to 5 | `Query(5, ge=1, le=10)` in `routes.py` |
| `skip` (stops) must be 0 or more | `Query(0, ge=0)` in `routes.py` |
| `destination` must be 3–30 characters and is required | `Query(..., min_length=3, max_length=30)` in `search.py` |
| `max_fare`, if given, must be greater than 0 | `Query(None, gt=0)` in `search.py` |

`RouteNumber` and `Plate` are each declared **once**, in `model.py`, and
imported wherever a route number or a plate shows up — `routes.py` uses
`RouteNumber` in three different endpoints without ever repeating
`ge=1, le=200`.

A route number in range that simply doesn't exist (e.g. `150`) is not
rubbish — that's a `404`. A well-formed search that matches nothing is
not an error either — that's a `200` with an empty `results` list.

## Design notes

- **The office rule.** `data.py` loads `lagos_routes.json` exactly once,
  in the `lifespan` handler in `main.py`, and caches it in memory. No
  endpoint touches the filesystem.
- **The types rule.** Every function parameter and return type is
  annotated; response shapes live in `model.py` as Pydantic models.
- **No `if`-thickets.** Range checks, pattern checks, and the enum of
  valid bus types are all declared in type annotations (`Path(...)`,
  `Query(...)`, `Enum`), not verified by hand inside function bodies.

## Demo slips

| Request | Expected |
|---|---|
| `GET /routes/0` | `422` — below the doorway's range |
| `GET /routes/150` | `404` — in range, but no such route |
| `GET /routes/34` | `200` |
| `GET /buses/banana` | `422` — doesn't match the plate shape |
| A well-shaped plate the union doesn't own | `404` |
| `GET /search?destination=aj` | `422` — under 3 characters |
| `GET /search?destination=Ajah&max_fare=500` | `200`, filtered |
| `GET /routes/34/stops?limit=50` | `422` — over the doorway's cap of 10 |
| `GET /fleet/okada` | `422` — not one of the three known kinds |

## Submission note

The `venv/` directory is intentionally left out of version control (see
`.gitignore` if you add one) — it's a local build artifact tied to one
machine's Python install, not part of the project itself.
