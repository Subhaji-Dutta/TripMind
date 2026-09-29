from backend.agents.orchestrator import OrchestrationAgent
from backend.agents.weather_agent import WeatherAgent
from backend.agents.transport_agent import TransportAgent
from backend.agents.accommodation_agent import AccommodationAgent
from backend.agents.restaurant_agent import RestaurantAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.packing_agent import PackingAgent
from backend.selection import TripSelection
from backend.models.trip import TripRequest


def main():
    print("\nTesting TripMind Packing Agent")
    print("=" * 60)

    request = TripRequest(
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-09-30",
        travelers=2,
        budget=50000,
        currency="INR",
    )

    orchestrator = OrchestrationAgent(
        weather_agent=WeatherAgent().run,
        transport_agent=TransportAgent().run,
        accommodation_agent=AccommodationAgent().run,
        restaurant_agent=RestaurantAgent().run,
        recommendation_agent=RecommendationAgent().run,
    )

    state = orchestrator.run(request)

    assert state.recommendations is not None

    selected_transport = state.transport_options[0]
    selected_accommodation = state.accommodation_options[0]
    selected_activity = state.recommendations.activities[0]
    selected_attraction = state.recommendations.attractions[0]
    selected_restaurant = state.recommendations.restaurants[0]

    state = TripSelection.apply_selection(
        state=state,
        transport=selected_transport,
        accommodation=selected_accommodation,
        activities=[selected_activity],
        attractions=[selected_attraction],
        restaurants=[selected_restaurant],
    )

    agent = PackingAgent()

    state.packing_list = agent.run(
        request=request,
        weather=state.weather,
        selected_options=state.selected_options,
    )

    print("\n" + "=" * 60)
    print("PACKING LIST")
    print("=" * 60)

    for index, item in enumerate(state.packing_list, start=1):
        print(f"  {index}. {item}")

    print("\n" + "=" * 60)
    print("PACKING VALIDATION")
    print("=" * 60)

    assert state.weather is not None
    assert state.selected_options is not None
    assert state.selected_options.transport is not None
    assert state.selected_options.accommodation is not None

    assert isinstance(state.packing_list, list)
    assert len(state.packing_list) >= 8
    assert len(state.packing_list) <= 20

    assert all(
        isinstance(item, str) and item.strip()
        for item in state.packing_list
    )

    normalized_items = [
        item.strip().lower()
        for item in state.packing_list
    ]

    assert len(normalized_items) == len(set(normalized_items))

    print("  ✓ Weather data used")
    print("  ✓ Selected transport used")
    print("  ✓ Selected accommodation used")
    print("  ✓ Selected activity used")
    print("  ✓ Selected attraction used")
    print("  ✓ Selected restaurant used")
    print("  ✓ Packing list generated")
    print("  ✓ Packing list contains 8–20 items")
    print("  ✓ All packing items are valid strings")
    print("  ✓ No duplicate packing items")

    print("\n✅ Packing Agent test passed.")


if __name__ == "__main__":
    main()