from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.restaurant_agent import RestaurantAgent

from backend.models.trip import (
    TripRequest,
    WeatherInfo,
    TransportOption,
    AccommodationOption,
)


def main():
    print("\nTesting TripMind Recommendation Agent")
    print("=" * 60)

    request = TripRequest(
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-09-30",
        travelers=2,
        budget=50000,
        currency="INR",
    )

    weather = WeatherInfo(
        destination="Goa",
        forecast=[
            {
                "date": "2026-09-27",
                "temperature_c": 25,
                "condition": "Light Drizzle",
                "rain_probability": 60,
            },
            {
                "date": "2026-09-28",
                "temperature_c": 25,
                "condition": "Partly Cloudy",
                "rain_probability": 20,
            },
            {
                "date": "2026-09-29",
                "temperature_c": 26,
                "condition": "Partly Cloudy",
                "rain_probability": 10,
            },
            {
                "date": "2026-09-30",
                "temperature_c": 27,
                "condition": "Mainly Clear",
                "rain_probability": 5,
            },
        ],
    )

    transport_options = [
        TransportOption(
            mode="Flight",
            provider="Demo Airways",
            departure="Kolkata",
            arrival="Goa",
            duration="2h 30m",
            estimated_cost=8500,
        ),
        TransportOption(
            mode="Train",
            provider="Demo Railways",
            departure="Kolkata",
            arrival="Goa",
            duration="10h 30m",
            estimated_cost=2200,
        ),
    ]

    accommodation_options = [
        AccommodationOption(
            name="Demo Beach Resort",
            location="Goa",
            rating=4.3,
            price_per_night=3500,
            total_cost=14000,
            amenities=[
                "Wi-Fi",
                "Swimming Pool",
                "Breakfast",
            ],
        ),
        AccommodationOption(
            name="Demo City Hotel",
            location="Goa",
            rating=4.1,
            price_per_night=2800,
            total_cost=11200,
            amenities=[
                "Wi-Fi",
                "Breakfast",
                "Air Conditioning",
            ],
        ),
    ]

    print("\nGetting restaurants from Restaurant Agent...")
    restaurant_agent = RestaurantAgent()
    restaurants = restaurant_agent.run(request)

    print("\nRestaurant Agent provided:")
    for restaurant in restaurants:
        print(
            f"  {restaurant.name} | "
            f"{restaurant.cuisine} | "
            f"{restaurant.price_range} | "
            f"₹{restaurant.estimated_cost:,.0f}"
        )

    available_restaurant_names = {
        restaurant.name
        for restaurant in restaurants
    }

    print("\nRunning Recommendation Agent...")
    recommendation_agent = RecommendationAgent()

    result = recommendation_agent.run(
        request=request,
        weather=weather,
        transport_options=transport_options,
        accommodation_options=accommodation_options,
        restaurants=restaurants,
    )

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    print(
        f"Recommended activities: "
        f"{len(result.activities)}"
    )

    for activity in result.activities:
        print(
            f"  {activity.name} | "
            f"{activity.category} | "
            f"{activity.duration} | "
            f"₹{activity.estimated_cost:,.0f}"
        )

    print(
        f"\nRecommended attractions: "
        f"{len(result.attractions)}"
    )

    for attraction in result.attractions:
        print(
            f"  {attraction.name} | "
            f"{attraction.category} | "
            f"{attraction.duration} | "
            f"₹{attraction.estimated_cost:,.0f}"
        )

    print(
        f"\nRecommended restaurants: "
        f"{len(result.restaurants)}"
    )

    for restaurant in result.restaurants:
        print(
            f"  {restaurant.name} | "
            f"{restaurant.cuisine} | "
            f"{restaurant.price_range} | "
            f"₹{restaurant.estimated_cost:,.0f}"
        )

    print("\n" + "=" * 60)
    print("RECOMMENDATION VALIDATION")
    print("=" * 60)

    assert len(result.activities) == 2
    print("  ✓ Exactly 2 activities returned")

    assert len(result.attractions) == 2
    print("  ✓ Exactly 2 attractions returned")

    assert len(result.restaurants) == 2
    print("  ✓ Exactly 2 restaurants returned")

    assert all(
        activity.name
        for activity in result.activities
    )
    print("  ✓ Activity names present")

    assert all(
        attraction.name
        for attraction in result.attractions
    )
    print("  ✓ Attraction names present")

    assert all(
        restaurant.name
        for restaurant in result.restaurants
    )
    print("  ✓ Restaurant names present")

    recommended_restaurant_names = {
        restaurant.name
        for restaurant in result.restaurants
    }

    assert recommended_restaurant_names.issubset(
        available_restaurant_names
    )
    print(
        "  ✓ Recommended restaurants come only "
        "from Restaurant Agent results"
    )

    print(
        "\nRestaurant contract verified:"
    )

    for restaurant in result.restaurants:
        print(
            f"  ✓ {restaurant.name} "
            f"was provided by Restaurant Agent"
        )

    print("\n✅ Recommendation Agent test passed.")


if __name__ == "__main__":
    main()