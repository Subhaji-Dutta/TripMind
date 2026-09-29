import json
import os
from typing import Dict

import redis
from dotenv import load_dotenv

from backend.models.trip import TripState


load_dotenv(".env.local")
load_dotenv(".env")


REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError("REDIS_URL is not configured.")


redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
)

TRIP_KEY_PREFIX = "tripmind:trip:"


def _trip_key(trip_id: str) -> str:
    return f"{TRIP_KEY_PREFIX}{trip_id}"


def save_trip(trip_id: str, state: TripState) -> None:
    data = state.model_dump(mode="json")

    redis_client.set(
        _trip_key(trip_id),
        json.dumps(data, ensure_ascii=False),
    )


def get_trip(trip_id: str) -> TripState:
    data = redis_client.get(_trip_key(trip_id))

    if data is None:
        raise KeyError(f"Trip not found: {trip_id}")

    trip_data = json.loads(data)

    # Backward compatibility for trips created
    # before the source field was added.
    request_data = trip_data.get("request", {})

    if "source" not in request_data:
        request_data["source"] = "Kolkata"

    return TripState.model_validate(trip_data)


def update_trip(trip_id: str, state: TripState) -> None:
    # Make sure the trip already exists.
    if redis_client.exists(_trip_key(trip_id)) == 0:
        raise KeyError(f"Trip not found: {trip_id}")

    save_trip(trip_id, state)