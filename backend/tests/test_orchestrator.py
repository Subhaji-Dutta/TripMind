from backend.agents.orchestrator import OrchestrationAgent

from backend.models.trip import (
    TripRequest,
    TripPreferences,
    WeatherInfo,
    TransportOption,
    AccommodationOption,
    Restaurant,
    RecommendationResult,
    Activity,
    Attraction,
)


# ============================================================
# MOCK WEATHER
# ============================================================

def mock_weather_agent(request):

    print("  [MOCK] Weather Agent called")

    return WeatherInfo(
        destination=request.destination,
        forecast=[
            {
                "date": request.start_date,
                "temperature_c": 30,
                "condition": "Sunny",
                "rain_probability": 20,
            }
        ],
    )


# ============================================================
# MOCK TRANSPORT
# ============================================================

def mock_transport_agent(request):

    print("  [MOCK] Transport Agent called")

    return [
        TransportOption(
            mode="Flight",
            provider="Demo Airways",
            departure="08:00",
            arrival="10:30",
            duration="2h 30m",
            estimated_cost=8500,
        ),
        TransportOption(
            mode="Train",
            provider="Demo Railways",
            departure="18:00",
            arrival="06:00",
            duration="12h",
            estimated_cost=2200,
        ),
    ]


# ============================================================
# MOCK ACCOMMODATION
# ============================================================

def mock_accommodation_agent(request):

    print("  [MOCK] Accommodation Agent called")

    return [
        AccommodationOption(
            name="Demo Beach Resort",
            location=request.destination,
            rating=4.3,
            price_per_night=3500,
            total_cost=14000,
            amenities=[
                "Wi-Fi",
                "Pool",
                "Breakfast",
            ],
        )
    ]


# ============================================================
# MOCK RESTAURANT
# ============================================================

def mock_restaurant_agent(request):

    print("  [MOCK] Restaurant Agent called")

    return [
        Restaurant(
            name="Demo Coastal Kitchen",
            location=request.destination,
            cuisine="Indian Seafood",
            price_range="₹₹",
            estimated_cost=800,
        ),
        Restaurant(
            name="Demo Heritage Cafe",
            location=request.destination,
            cuisine="Indian",
            price_range="₹₹",
            estimated_cost=600,
        ),
    ]


# ============================================================
# MOCK RECOMMENDATION AGENT
# ============================================================

def mock_recommendation_agent(
    request,
    weather,
    transport_options,
    accommodation_options,
    restaurants,
):

    print("  [MOCK] Recommendation Agent called")

    # Verify that the recommendation agent receives
    # all information collected by the orchestrator.

    assert request.destination == "Goa"
    assert weather is not None
    assert len(transport_options) > 0
    assert len(accommodation_options) > 0
    assert len(restaurants) > 0

    return RecommendationResult(
        activities=[
            Activity(
                name="Beach Day",
                location="North Goa",
                category="Beach",
                estimated_cost=500,
                duration="4 hours",
                description="Relax and enjoy the beach.",
            )
        ],
        attractions=[
            Attraction(
                name="Fort Aguada",
                location="Goa",
                category="Heritage",
                estimated_cost=50,
                duration="2 hours",
                description="Historic Portuguese fort.",
                available_days=[],
                opening_hours="09:00-18:00",
            )
        ],
        restaurants=restaurants,
    )


# ============================================================
# TEST
# ============================================================

def main():

    print("\nTesting TripMind Orchestration Agent")

    request = TripRequest(
        destination="Goa",
        start_date="2026-11-10",
        end_date="2026-11-14",
        travelers=2,
        budget=50000,
        currency="INR",
        preferences=TripPreferences(
            interests=[
                "beaches",
                "culture",
                "nature",
            ],
            accommodation_type="comfortable",
            transport_preference="any",
            food_preferences=[
                "Indian",
                "seafood",
            ],
            travel_pace="balanced",
        ),
    )

    orchestrator = OrchestrationAgent(
        weather_agent=mock_weather_agent,
        transport_agent=mock_transport_agent,
        accommodation_agent=mock_accommodation_agent,
        restaurant_agent=mock_restaurant_agent,
        recommendation_agent=mock_recommendation_agent,
    )

    state = orchestrator.run(request)

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    print(
        f"\nWeather: "
        f"{len(state.weather.forecast)} forecast entry"
    )

    print(
        f"Transport options: "
        f"{len(state.outbound_transport_options) + len(state.return_transport_options)}"
    )

    print(
        f"Accommodation options: "
        f"{len(state.accommodation_options)}"
    )

    print(
        f"Restaurant options: "
        f"{len(state.restaurants)}"
    )

    print(
        f"Recommended activities: "
        f"{len(state.recommendations.activities)}"
    )

    print(
        f"Recommended attractions: "
        f"{len(state.recommendations.attractions)}"
    )

    print("\n✅ Orchestration Agent test passed.")


if __name__ == "__main__":
    main()