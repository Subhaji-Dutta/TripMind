from backend.agents.accommodation_agent import AccommodationAgent
from backend.models.trip import TripRequest


def main():
    print("\nTesting TripMind Accommodation Agent")
    print("=" * 60)

    request = TripRequest(
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-10-01",
        travelers=2,
        budget=50000,
        currency="INR",
    )

    agent = AccommodationAgent()
    results = agent.run(request)

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    print(f"Accommodation options: {len(results)}")

    for accommodation in results:
        print(
            f"  {accommodation.name} | "
            f"{accommodation.location} | "
            f"Rating: {accommodation.rating} | "
            f"₹{accommodation.price_per_night:,.0f}/night | "
            f"Total: ₹{accommodation.total_cost:,.0f}"
        )

        print(
            f"    Amenities: "
            f"{', '.join(accommodation.amenities)}"
        )

    print("\n" + "=" * 60)
    print("ACCOMMODATION VALIDATION")
    print("=" * 60)

    assert len(results) == 2

    for accommodation in results:
        assert accommodation.name
        assert accommodation.location
        assert accommodation.rating is not None
        assert 1 <= accommodation.rating <= 5
        assert accommodation.price_per_night > 0
        assert accommodation.total_cost > 0
        assert len(accommodation.amenities) > 0

        expected_total = accommodation.price_per_night * 4

        assert accommodation.total_cost == expected_total

    print("  ✓ Exactly 2 accommodations returned")
    print("  ✓ Accommodation names present")
    print("  ✓ Locations present")
    print("  ✓ Ratings are valid")
    print("  ✓ Nightly prices are valid")
    print("  ✓ Total costs are valid")
    print("  ✓ Amenities are present")
    print("  ✓ Total = nightly price × 4 nights")

    print("\n✅ Accommodation Agent test passed.")


if __name__ == "__main__":
    main()