from backend.agents.orchestrator import OrchestrationAgent

from backend.models.trip import (
    TripRequest,
    WeatherInfo,
    TransportOption,
    AccommodationOption,
    Restaurant,
    RecommendationResult,
    Activity,
    Attraction,
)


def fake_weather_agent(request):
    return WeatherInfo(
        destination=request.destination,
        forecast=[
            {
                "date": request.start_date,
                "temperature_c": 26,
                "condition": "Sunny",
                "rain_probability": 10,
            }
        ],
    )


def fake_transport_agent(request):
    outbound = [
        TransportOption(
            mode="Train",
            provider="Test Railways",
            departure=request.source,
            arrival=request.destination,
            duration="30 hours",
            estimated_cost=2500,
        )
    ]

    return_transport = [
        TransportOption(
            mode="Train",
            provider="Test Railways",
            departure=request.destination,
            arrival=request.source,
            duration="30 hours",
            estimated_cost=2500,
        )
    ]

    return outbound, return_transport


def fake_accommodation_agent(request):
    return [
        AccommodationOption(
            name="Test Beach Hotel",
            location=request.destination,
            rating=4.2,
            price_per_night=3000,
            total_cost=9000,
            amenities=["Wi-Fi"],
        )
    ]


def fake_restaurant_agent(request):
    return [
        Restaurant(
            name="Test Restaurant",
            location=request.destination,
            cuisine="Indian",
            price_range="₹₹",
            estimated_cost=800,
        )
    ]


def fake_recommendation_agent(
    request,
    weather,
    transport_options,
    accommodation_options,
):
    """
    The important part of this fake agent is its signature.

    It accepts:
    - request
    - weather
    - transport options
    - accommodation options

    It does NOT accept restaurants.
    """

    assert request.destination == "Goa"

    assert weather.destination == "Goa"

    assert len(transport_options) == 2

    assert len(accommodation_options) == 1

    return RecommendationResult(
        activities=[
            Activity(
                name="Beach Yoga",
                location="Goa",
                category="Wellness",
                estimated_cost=500,
                duration="1 hour",
                description="Yoga near the beach.",
            )
        ],
        attractions=[
            Attraction(
                name="Fort Aguada",
                location="Goa",
                category="Historical",
                estimated_cost=100,
                duration="2 hours",
                description="Historic fort.",
                available_days=[],
                opening_hours="9 AM - 6 PM",
            )
        ],
    )


def main():
    print("\nTesting TripMind Orchestration Agent")
    print("=" * 60)

    request = TripRequest(
        source="Kolkata",
        destination="Goa",
        start_date="2026-10-10",
        end_date="2026-10-12",
        travelers=2,
        budget=50000,
        currency="INR",
    )

    orchestrator = OrchestrationAgent(
        weather_agent=fake_weather_agent,
        transport_agent=fake_transport_agent,
        accommodation_agent=fake_accommodation_agent,
        restaurant_agent=fake_restaurant_agent,
        recommendation_agent=fake_recommendation_agent,
    )

    print("\nRunning orchestration...")

    state = orchestrator.run(request)

    print("\n" + "=" * 60)
    print("ORCHESTRATION VALIDATION")
    print("=" * 60)

    assert state.request.destination == "Goa"
    print("  ✓ Trip request stored")

    assert state.weather is not None
    print("  ✓ Weather stored independently")

    assert len(state.outbound_transport_options) == 1
    print("  ✓ Outbound transport stored")

    assert len(state.return_transport_options) == 1
    print("  ✓ Return transport stored")

    assert len(state.accommodation_options) == 1
    print("  ✓ Accommodation stored")

    assert len(state.restaurants) == 1
    print("  ✓ Restaurants stored independently")

    assert state.recommendations is not None
    print("  ✓ Recommendation result stored")

    assert len(state.recommendations.activities) == 1
    print("  ✓ Activities received from Recommendation Agent")

    assert len(state.recommendations.attractions) == 1
    print("  ✓ Attractions received from Recommendation Agent")

    print("\nArchitecture validation:")

    print(
        "  ✓ Restaurant Agent output remains in state.restaurants"
    )

    print(
        "  ✓ Recommendation Agent receives no restaurant data"
    )

    print(
        "  ✓ Recommendation Agent produces activities"
    )

    print(
        "  ✓ Recommendation Agent produces attractions"
    )

    print(
        "  ✓ Orchestrator keeps agent responsibilities separate"
    )

    print("\n✅ Orchestration Agent test passed.")


if __name__ == "__main__":
    main()