from datetime import date, timedelta

from backend.agents.orchestrator import OrchestrationAgent
from backend.agents.weather_agent import WeatherAgent
from backend.agents.transport_agent import TransportAgent
from backend.agents.accommodation_agent import AccommodationAgent
from backend.agents.restaurant_agent import RestaurantAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.packing_agent import PackingAgent
from backend.agents.itinerary_agent import ItineraryAgent
from backend.selection import TripSelection
from backend.models.trip import TripRequest


def main():
    print("\nTesting TripMind Itinerary Agent")
    print("=" * 60)

    request = TripRequest(
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

    assert state.weather is not None
    assert state.recommendations is not None

    # --------------------------------------------------
    # USER SELECTION
    # --------------------------------------------------

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

    assert state.selected_options is not None

    # --------------------------------------------------
    # PACKING AGENT
    # --------------------------------------------------

    packing_agent = PackingAgent()

    state.packing_list = packing_agent.run(
        request=request,
        weather=state.weather,
        selected_options=state.selected_options,
    )

    # --------------------------------------------------
    # ITINERARY AGENT
    # --------------------------------------------------

    itinerary_agent = ItineraryAgent()

    state.final_itinerary = itinerary_agent.run(
        request=request,
        weather=state.weather,
        selected_options=state.selected_options,
        packing_list=state.packing_list,
    )

    # --------------------------------------------------
    # DISPLAY ITINERARY
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL ITINERARY")
    print("=" * 60)

    itinerary = state.final_itinerary

    print(f"Destination: {itinerary['destination']}")
    print(
        f"Dates: {itinerary['start_date']} "
        f"→ {itinerary['end_date']}"
    )
    print(f"Travelers: {itinerary['travelers']}")

    print("\nDaily Plan:")

    for day in itinerary["days"]:
        weather = day.get("weather", {})

        print(f"\n  {day['date']}")

        print(
            f"    Weather: "
            f"{weather.get('temperature_c')}°C | "
            f"{weather.get('condition')} | "
            f"Rain: {weather.get('rain_probability')}%"
        )

        morning = day.get("morning")
        afternoon = day.get("afternoon")
        evening = day.get("evening")

        if morning:
            print(
                f"    Morning: "
                f"{morning.get('name')}"
            )

        if afternoon:
            print(
                f"    Afternoon: "
                f"{afternoon.get('name')}"
            )

        if evening:
            print(
                f"    Evening: "
                f"{evening.get('name')}"
            )

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("ITINERARY VALIDATION")
    print("=" * 60)

    assert isinstance(itinerary, dict)

    assert itinerary["destination"] == request.destination
    assert itinerary["start_date"] == request.start_date
    assert itinerary["end_date"] == request.end_date
    assert itinerary["travelers"] == request.travelers

    assert isinstance(itinerary["days"], list)

    # Number of itinerary days:
    # start date included, end date excluded.
    start = date.fromisoformat(request.start_date)
    end = date.fromisoformat(request.end_date)

    expected_days = (end - start).days+1

    assert len(itinerary["days"]) == expected_days

    # --------------------------------------------------
    # DATE VALIDATION
    # --------------------------------------------------

    expected_dates = [
        (start + timedelta(days=index)).isoformat()
        for index in range(expected_days)
    ]

    actual_dates = [
        day["date"]
        for day in itinerary["days"]
    ]

    assert actual_dates == expected_dates

    # --------------------------------------------------
    # DAILY PLAN VALIDATION
    # --------------------------------------------------

    for day in itinerary["days"]:
        assert day["date"]

        assert "weather" in day
        assert isinstance(day["weather"], dict)

        weather = day["weather"]

        assert "temperature_c" in weather
        assert "condition" in weather
        assert "rain_probability" in weather

        if day.get("morning") is not None:
            assert day["morning"]["name"]

        if day.get("afternoon") is not None:
            assert day["afternoon"]["name"]

        if day.get("evening") is not None:
            assert day["evening"]["name"]

    # --------------------------------------------------
    # SELECTED OPTIONS MUST BE REPRESENTED
    # --------------------------------------------------

    selected_activity_name = selected_activity.name
    selected_attraction_name = selected_attraction.name
    selected_restaurant_name = selected_restaurant.name

    itinerary_text = str(itinerary)

    assert selected_activity_name in itinerary_text
    assert selected_attraction_name in itinerary_text
    assert selected_restaurant_name in itinerary_text

    print("  ✓ Destination is correct")
    print("  ✓ Start date is correct")
    print("  ✓ End date is correct")
    print("  ✓ Traveler count is correct")
    print("  ✓ Correct number of daily plans generated")
    print("  ✓ Daily dates are chronological")
    print("  ✓ Weather data is included")
    print("  ✓ Weather data contains temperature")
    print("  ✓ Weather data contains condition")
    print("  ✓ Weather data contains rain probability")
    print("  ✓ Selected activity is included")
    print("  ✓ Selected attraction is included")
    print("  ✓ Selected restaurant is included")

    print("\n" + "=" * 60)
    print("FINAL FLOW VALIDATION")
    print("=" * 60)

    assert state.weather is not None
    assert state.transport_options
    assert state.accommodation_options
    assert state.restaurants
    assert state.recommendations is not None
    assert state.selected_options is not None
    assert state.packing_list
    assert state.final_itinerary is not None

    print("  ✓ Weather Agent")
    print("  ✓ Transport Agent")
    print("  ✓ Accommodation Agent")
    print("  ✓ Restaurant Agent")
    print("  ✓ Recommendation Agent")
    print("  ✓ User Selection")
    print("  ✓ Packing Agent")
    print("  ✓ Itinerary Agent")

    print("\n✅ Itinerary Agent test passed.")
    print("✅ Complete TripMind planning flow passed.")


if __name__ == "__main__":
    main()