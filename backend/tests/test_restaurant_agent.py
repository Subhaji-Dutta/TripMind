from backend.agents.restaurant_agent import RestaurantAgent
from backend.models.trip import TripRequest


def main():
    print("\nTesting TripMind Restaurant Agent")
    print("=" * 60)

    request = TripRequest(
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-09-30",
        travelers=2,
        budget=50000,
        currency="INR",
    )

    agent = RestaurantAgent()
    results = agent.run(request)

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    print(f"Restaurant options: {len(results)}")

    for restaurant in results:
        print(
            f"  {restaurant.name} | "
            f"{restaurant.location} | "
            f"{restaurant.cuisine} | "
            f"{restaurant.price_range} | "
            f"₹{restaurant.estimated_cost:,.0f}"
        )

    print("\n" + "=" * 60)
    print("RESTAURANT VALIDATION")
    print("=" * 60)

    assert len(results) == 3

    for restaurant in results:
        assert restaurant.name
        assert restaurant.location
        assert restaurant.cuisine
        assert restaurant.price_range
        assert restaurant.estimated_cost > 0

    print("  ✓ Exactly 3 restaurants returned")
    print("  ✓ Restaurant names present")
    print("  ✓ Locations present")
    print("  ✓ Cuisine information present")
    print("  ✓ Price ranges present")
    print("  ✓ Estimated costs are valid")

    print("\n✅ Restaurant Agent test passed.")


if __name__ == "__main__":
    main()