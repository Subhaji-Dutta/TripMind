from typing import Callable, Optional

from backend.models.trip import TripRequest, TripState


class OrchestrationAgent:
    """
    Main controller for the TripMind planning workflow.

    This component does NOT use an LLM.

    Its responsibility is to:

    1. Receive the user's trip request.
    2. Call the required data-provider agents.
    3. Collect their results.
    4. Pass the relevant information to the
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
        Call the independent data-provider agents and store
        their results in TripState.
        """

        # ----------------------------------------------------
        # Weather Agent
        # ----------------------------------------------------

        if self.weather_agent is not None:
            state.weather = self.weather_agent(
                state.request
            )

        # ----------------------------------------------------
        # Transport Agent
        # ----------------------------------------------------

        if self.transport_agent is not None:
            (
                state.outbound_transport_options,
                state.return_transport_options,
            ) = self.transport_agent(
                state.request
            )

        # ----------------------------------------------------
        # Accommodation Agent
        # ----------------------------------------------------

        if self.accommodation_agent is not None:
            state.accommodation_options = (
                self.accommodation_agent(
                    state.request
                )
            )

        # ----------------------------------------------------
        # Restaurant Agent
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
        Send only the information required by the
        Recommendation Agent.

        The Recommendation Agent generates:
        - Activities
        - Attractions

        Restaurants are handled independently by the
        Restaurant Agent and remain in TripState.
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
        Run the complete orchestration workflow.
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
            f"{request.currency} "
            f"{request.budget:,.2f}"
        )

        # ----------------------------------------------------
        # Step 1: Create initial state
        # ----------------------------------------------------

        state = self.create_state(request)

        # ----------------------------------------------------
        # Step 2: Collect information from independent agents
        # ----------------------------------------------------

        print("\nCollecting trip information...")

        state = self.collect_trip_data(state)

        # ----------------------------------------------------
        # Step 3: Generate activity and attraction candidates
        # ----------------------------------------------------

        print(
            "\nSending trip information "
            "to Recommendation Agent..."
        )

        state = self.create_recommendations(state)

        print("\nOrchestration completed.")

        return state