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
from backend.planning_engine import PlanningEngine


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

planning_engine = PlanningEngine()

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
    # 1. Run agents ONCE
    state = orchestrator.run(request)

    # 2. Create trip ID
    trip_id = str(uuid.uuid4())

    # 3. Save complete agent-generated data to Redis
    save_trip(trip_id, state)

    # 4. Read the saved state from Redis
    state = get_trip(trip_id)

    # 5. Generate planning options using cached data
    state.planning_result = planning_engine.run(state)

    # 6. Save planning result to Redis
    update_trip(trip_id, state)

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

    # ============================================================
    # LOAD TRIP FROM REDIS
    # ============================================================

    try:

        state = get_trip(
            selection.trip_id
        )

    except KeyError:

        raise HTTPException(
            status_code=404,
            detail=(
                "Trip not found. "
                "The trip_id may be invalid or expired."
            ),
        )

    # ============================================================
    # APPLY USER SELECTIONS
    # ============================================================

    try:

        state = TripSelection.apply_selection(
            state=state,

            outbound_transport=(
                selection.outbound_transport
            ),

            return_transport=(
                selection.return_transport
            ),

            accommodation=(
                selection.accommodation
            ),

            activities=(
                selection.activities
            ),

            attractions=(
                selection.attractions
            ),

            restaurants=(
                selection.restaurants
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # ============================================================
    # CLEAR PREVIOUS FINAL TRIP PLAN
    # ============================================================
    #
    # The user has changed their selections.
    #
    # Therefore the previous:
    #   - packing list
    #   - itinerary
    #   - final budget
    #
    # are no longer valid.
    #
    # They will be regenerated only when the user clicks:
    #
    # "Generate My Final Trip Plan"
    #
    # ============================================================

    state.packing_list = []

    state.final_itinerary = None

    state.budget_summary = None

    # ============================================================
    # RECALCULATE PLANNING OPTIONS
    # ============================================================
    #
    # This is deterministic Python.
    #
    # It does NOT call:
    #   - Transport Agent
    #   - Accommodation Agent
    #   - Restaurant Agent
    #   - Recommendation Agent
    #   - Packing Agent
    #   - Itinerary Agent
    #
    # It uses the already cached trip data.
    #
    # ============================================================

    state.planning_result = (
        planning_engine.run(state)
    )

    # ============================================================
    # SAVE UPDATED STATE TO REDIS
    # ============================================================

    update_trip(
        selection.trip_id,
        state,
    )

    # ============================================================
    # RETURN UPDATED SELECTION + PLANNING
    # ============================================================

    return {
        "trip_id": selection.trip_id,

        "selected_options": (
            state.selected_options.model_dump()
        ),

        "planning_result": (
            state.planning_result.model_dump()
        ),
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