from backend.agents.orchestrator import OrchestrationAgent
from backend.agents.weather_agent import WeatherAgent
from backend.agents.transport_agent import TransportAgent
from backend.agents.accommodation_agent import AccommodationAgent
from backend.agents.restaurant_agent import RestaurantAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.selection import TripSelection
from backend.models.trip import TripRequest


def main():

    print("\nTesting TripMind User Selection Layer")
    print("=" * 60)

    request = TripRequest(
        source="Delhi",
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-09-30",
        travelers=2,
        budget=50000,
        currency="INR",
    )

    # --------------------------------------------------
    # ORCHESTRATION
    # --------------------------------------------------

    orchestrator = OrchestrationAgent(
        weather_agent=WeatherAgent().run,
        transport_agent=TransportAgent().run,
        accommodation_agent=AccommodationAgent().run,
        restaurant_agent=RestaurantAgent().run,
        recommendation_agent=RecommendationAgent().run,
    )

    state = orchestrator.run(request)

    # --------------------------------------------------
    # PRE-SELECTION VALIDATION
    # --------------------------------------------------

    assert state.recommendations is not None
    assert state.outbound_transport_options
    assert state.return_transport_options
    assert state.accommodation_options
    assert state.recommendations.activities
    assert state.recommendations.attractions
    assert state.recommendations.restaurants

    # --------------------------------------------------
    # SIMULATE USER SELECTION
    # --------------------------------------------------

    selected_outbound_transport = (
        state.outbound_transport_options[0]
    )

    selected_return_transport = (
        state.return_transport_options[0]
    )

    selected_accommodation = (
        state.accommodation_options[0]
    )

    selected_activity = (
        state.recommendations.activities[0]
    )

    selected_attraction = (
        state.recommendations.attractions[0]
    )

    selected_restaurant = (
        state.recommendations.restaurants[0]
    )

    print("\n" + "=" * 60)
    print("USER SELECTION")
    print("=" * 60)

    print(
        f"Outbound Transport: "
        f"{selected_outbound_transport.mode} - "
        f"{selected_outbound_transport.provider}"
    )

    print(
        f"Return Transport: "
        f"{selected_return_transport.mode} - "
        f"{selected_return_transport.provider}"
    )

    print(
        f"Accommodation: "
        f"{selected_accommodation.name}"
    )

    print(
        f"Activity: "
        f"{selected_activity.name}"
    )

    print(
        f"Attraction: "
        f"{selected_attraction.name}"
    )

    print(
        f"Restaurant: "
        f"{selected_restaurant.name}"
    )

    # --------------------------------------------------
    # APPLY SELECTION
    # --------------------------------------------------

    state = TripSelection.apply_selection(
        state=state,
        outbound_transport=selected_outbound_transport,
        return_transport=selected_return_transport,
        accommodation=selected_accommodation,
        activities=[selected_activity],
        attractions=[selected_attraction],
        restaurants=[selected_restaurant],
    )

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("SELECTION VALIDATION")
    print("=" * 60)

    assert state.selected_options is not None

    selected = state.selected_options

    # Outbound Transport
    assert (
        selected.outbound_transport
        is selected_outbound_transport
    )

    # Return Transport
    assert (
        selected.return_transport
        is selected_return_transport
    )

    # Accommodation
    assert (
        selected.accommodation
        is selected_accommodation
    )

    # Activity
    assert len(selected.activities) == 1
    assert (
        selected.activities[0]
        is selected_activity
    )

    # Attraction
    assert len(selected.attractions) == 1
    assert (
        selected.attractions[0]
        is selected_attraction
    )

    # Restaurant
    assert len(selected.restaurants) == 1
    assert (
        selected.restaurants[0]
        is selected_restaurant
    )

    print("  ✓ Outbound transport selection stored correctly")
    print("  ✓ Return transport selection stored correctly")
    print("  ✓ Accommodation selection stored correctly")
    print("  ✓ Activity selection stored correctly")
    print("  ✓ Attraction selection stored correctly")
    print("  ✓ Restaurant selection stored correctly")

    print("\n" + "=" * 60)
    print("SELECTED OPTIONS")
    print("=" * 60)

    print(
        f"  Outbound Transport : "
        f"{selected.outbound_transport.mode}"
    )

    print(
        f"  Return Transport   : "
        f"{selected.return_transport.mode}"
    )

    print(
        f"  Accommodation      : "
        f"{selected.accommodation.name}"
    )

    print(
        f"  Activity           : "
        f"{selected.activities[0].name}"
    )

    print(
        f"  Attraction         : "
        f"{selected.attractions[0].name}"
    )

    print(
        f"  Restaurant         : "
        f"{selected.restaurants[0].name}"
    )

    print("\n✅ User Selection test passed.")


if __name__ == "__main__":
    main()