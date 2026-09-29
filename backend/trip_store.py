import json
from pathlib import Path
from typing import Dict

from backend.models.trip import TripState


DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_FILE = DATA_DIR / "trips.json"


def _load_trips() -> Dict[str, TripState]:
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}

    trips = {}

    for trip_id, trip_data in data.items():
        # Backward compatibility for trips created
        # before the source field was added.
        if "source" not in trip_data.get("request", {}):
            trip_data["request"]["source"] = "Kolkata"

        trips[trip_id] = TripState.model_validate(trip_data)

    return trips


def _save_trips(trips: Dict[str, TripState]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        trip_id: state.model_dump(mode="json")
        for trip_id, state in trips.items()
    }

    temp_file = DATA_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    temp_file.replace(DATA_FILE)


def save_trip(trip_id: str, state: TripState) -> None:
    trips = _load_trips()
    trips[trip_id] = state
    _save_trips(trips)


def get_trip(trip_id: str) -> TripState:
    trips = _load_trips()

    if trip_id not in trips:
        raise KeyError(f"Trip not found: {trip_id}")

    return trips[trip_id]


def update_trip(trip_id: str, state: TripState) -> None:
    trips = _load_trips()

    if trip_id not in trips:
        raise KeyError(f"Trip not found: {trip_id}")

    trips[trip_id] = state
    _save_trips(trips)