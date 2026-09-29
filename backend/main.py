import uuid

from fastapi import FastAPI, HTTPException

from backend.agents.accommodation_agent import AccommodationAgent
from backend.agents.orchestrator import OrchestrationAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.restaurant_agent import RestaurantAgent
from backend.agents.transport_agent import TransportAgent
from backend.agents.weather_agent import WeatherAgent
from backend.models.trip import TripRequest, TripSelectionRequest
from backend.selection import TripSelection
from backend.trip_store import get_trip, save_trip, update_trip
from backend.agents.packing_agent import PackingAgent
from backend.agents.itinerary_agent import ItineraryAgent
from backend.budget import BudgetCalculator


app = FastAPI(
    title="TripMind API",
    description="Multi-Agent AI Travel Planner",
    version="1.0.0",
)


weather_agent = WeatherAgent()
transport_agent = TransportAgent()
accommodation_agent = AccommodationAgent()
restaurant_agent = RestaurantAgent()
recommendation_agent = RecommendationAgent()
packing_agent = PackingAgent()
itinerary_agent = ItineraryAgent()

orchestrator = OrchestrationAgent(
    weather_agent=weather_agent.run,
    transport_agent=transport_agent.run,
    accommodation_agent=accommodation_agent.run,
    restaurant_agent=restaurant_agent.run,
    recommendation_agent=recommendation_agent.run,
)


@app.get("/")
def root():
    return {
        "message": "TripMind API is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/api/trip/plan")
def create_trip_plan(request: TripRequest):
    state = orchestrator.run(request)

    trip_id = str(uuid.uuid4())

    save_trip(trip_id, state)

    return {
        "trip_id": trip_id,
        "trip": state.model_dump(),
    }

@app.get("/api/trip/{trip_id}")
def get_trip_details(trip_id: str):
    try:
        state = get_trip(trip_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Trip not found. The trip_id may be invalid or expired.",
        )

    return {
        "trip_id": trip_id,
        "trip": state.model_dump(),
    }


@app.post("/api/trip/select")
def select_trip_options(selection: TripSelectionRequest):
    try:
        state = get_trip(selection.trip_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Trip not found. The trip_id may be invalid or expired.",
        )
    try:
        state = TripSelection.apply_selection(
            state=state,
            outbound_transport=selection.outbound_transport,
            return_transport=selection.return_transport,
            accommodation=selection.accommodation,
            activities=selection.activities,
            attractions=selection.attractions,
            restaurants=selection.restaurants,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    update_trip(selection.trip_id, state)

    return {
        "trip_id": selection.trip_id,
        "selected_options": state.selected_options.model_dump(),
    }

@app.post("/api/trip/finalize")
def finalize_trip(trip_id: str):
    try:
        state = get_trip(trip_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Trip not found. The trip_id may be invalid or expired.",
        )

    if state.selected_options is None:
        raise HTTPException(
            status_code=400,
            detail="Trip options must be selected before finalizing.",
        )

    print("\nGenerating packing list...")
    state.packing_list = packing_agent.run(
        state.request,
        state.weather,
        state.selected_options,
    )

    print("\nGenerating final itinerary...")
    state.final_itinerary = itinerary_agent.run(
        state.request,
        state.weather,
        state.selected_options,
        state.packing_list,
    )

    print("\nCalculating budget summary...")
    state.budget_summary = BudgetCalculator.calculate(state)

    update_trip(trip_id, state)

    return {
        "trip_id": trip_id,
        "packing_list": state.packing_list,
        "final_itinerary": state.final_itinerary,
        "budget_summary": state.budget_summary,
    }

    update_trip(trip_id, state)

    return {
        "trip_id": trip_id,
        "packing_list": state.packing_list,
        "final_itinerary": state.final_itinerary,
    }