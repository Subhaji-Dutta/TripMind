from typing import Callable, Optional, Any

from backend.models.trip import (
    TripRequest,
    TripState,
    WeatherInfo,
    TransportOption,
    AccommodationOption,
    Restaurant,
    RecommendationResult,
)


class OrchestrationAgent:
    """
    Main controller for the TripMind planning workflow.

    This component does NOT use an LLM.

    Its responsibility is to:
    1. Receive the user's trip request.
    2. Call the required data-provider agents.
    3. Collect their results.
    4. Pass the collected information to the
       Recommendation Agent.
    """

    def __init__(
        self,
        weather_agent: Optional[Callable] = None,
        transport_agent: Optional[Callable] = None,
        accommodation_agent: Optional[Callable] = None,
        restaurant_agent: Optional[Callable] = None,
        recommendation_agent: Optional[Callable] = None,
    ):
        self.weather_agent = weather_agent
        self.transport_agent = transport_agent
        self.accommodation_agent = accommodation_agent
        self.restaurant_agent = restaurant_agent
        self.recommendation_agent = recommendation_agent

    # ========================================================
    # CREATE INITIAL STATE
    # ========================================================

    def create_state(self, request: TripRequest) -> TripState:
        """
        Create the initial TripState from the user's request.
        """

        return TripState(
            request=request
        )

    # ========================================================
    # COLLECT DATA
    # ========================================================

    def collect_trip_data(
        self,
        state: TripState,
    ) -> TripState:
        """
        Call the data-provider agents and store their
        results in TripState.

        The agents are optional for now because they will
        be implemented one at a time.
        """

        # ----------------------------------------------------
        # Weather
        # ----------------------------------------------------

        if self.weather_agent is not None:
            state.weather = self.weather_agent(
                state.request
            )

        # ----------------------------------------------------
        # Transport
        # ----------------------------------------------------

        if self.transport_agent is not None:
            (
                state.outbound_transport_options,
                state.return_transport_options,

            )= self.transport_agent(
                state.request
            )

        # ----------------------------------------------------
        # Accommodation
        # ----------------------------------------------------

        if self.accommodation_agent is not None:
            state.accommodation_options = (
                self.accommodation_agent(
                    state.request
                )
            )

        # ----------------------------------------------------
        # Restaurants
        # ----------------------------------------------------

        if self.restaurant_agent is not None:
            state.restaurants = self.restaurant_agent(
                state.request
            )

        return state

    # ========================================================
    # SEND DATA TO RECOMMENDATION AGENT
    # ========================================================

    def create_recommendations(
        self,
        state: TripState,
    ) -> TripState:
        """
        Send the user's request and all collected information
        to the Recommendation Agent.
        """

        if self.recommendation_agent is None:
            return state

        recommendations = self.recommendation_agent(
            state.request,
            state.weather,
            (
                state.outbound_transport_options
                + state.return_transport_options
            ),
            state.accommodation_options,
            state.restaurants,
        )

        state.recommendations = recommendations

        return state

    # ========================================================
    # MAIN ORCHESTRATION
    # ========================================================

    def run(
        self,
        request: TripRequest,
    ) -> TripState:
        """
        Run the orchestration workflow.
        """

        print("\n" + "=" * 60)
        print("TRIPMIND ORCHESTRATION")
        print("=" * 60)

        print(
            f"\nDestination : {request.destination}"
        )

        print(
            f"Dates       : "
            f"{request.start_date} → {request.end_date}"
        )

        print(
            f"Travelers   : {request.travelers}"
        )

        print(
            f"Budget      : "
            f"{request.currency} {request.budget:,.2f}"
        )

        # ----------------------------------------------------
        # Step 1: Create state
        # ----------------------------------------------------

        state = self.create_state(request)

        # ----------------------------------------------------
        # Step 2: Collect external information
        # ----------------------------------------------------

        print("\nCollecting trip information...")

        state = self.collect_trip_data(state)

        # ----------------------------------------------------
        # Step 3: Create recommendations
        # ----------------------------------------------------

        print(
            "\nSending collected information "
            "to Recommendation Agent..."
        )

        state = self.create_recommendations(state)

        print("\nOrchestration completed.")

        return state