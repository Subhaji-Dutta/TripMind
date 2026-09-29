from backend.budget import BudgetCalculator

from backend.models.trip import (
    TripRequest,
    TripPreferences,
    TripState,
    SelectedTripOptions,
    TransportOption,
    AccommodationOption,
    Activity,
    Attraction,
    Restaurant,
)


def main():

    print("\nTesting TripMind Budget Calculator")
    print("=" * 60)

    request = TripRequest(
        source="Delhi",
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-09-30",
        travelers=2,
        budget=50000,
        currency="INR",
        preferences=TripPreferences(
            interests=["beaches", "food"],
            accommodation_type="comfortable",
            transport_preference="any",
            food_preferences=["seafood"],
            travel_pace="balanced",
        ),
    )

    state = TripState(
        request=request,

        selected_options=SelectedTripOptions(

            # ------------------------------------------
            # OUTBOUND
            # Delhi → Goa
            # ₹12,000/person
            # ------------------------------------------
            outbound_transport=TransportOption(
                mode="Bus",
                provider="RedBus",
                departure="Delhi",
                arrival="Goa",
                duration="30h",
                estimated_cost=12000,
            ),

            # ------------------------------------------
            # RETURN
            # Goa → Delhi
            # ₹5,000/person
            # ------------------------------------------
            return_transport=TransportOption(
                mode="Train",
                provider="Indian Railways",
                departure="Goa",
                arrival="Delhi",
                duration="30h",
                estimated_cost=5000,
            ),

            accommodation=AccommodationOption(
                name="Baga Beach Retreat",
                location="Baga, Goa",
                rating=4.3,
                price_per_night=5500,
                total_cost=16500,
                amenities=["Wi-Fi", "Breakfast"],
            ),

            activities=[
                Activity(
                    name="Cooking Class",
                    location="Baga",
                    category="Food",
                    estimated_cost=800,
                    duration="3 hours",
                )
            ],

            attractions=[
                Attraction(
                    name="Baga Beach",
                    location="Baga",
                    category="Beach",
                    estimated_cost=0,
                    duration="3 hours",
                )
            ],

            restaurants=[
                Restaurant(
                    name="Fisherman's Wharf",
                    location="Calangute",
                    cuisine="Goan Seafood",
                    price_range="₹₹₹",
                    estimated_cost=1200,
                )
            ],
        ),
    )

    result = BudgetCalculator.calculate(state)

    print("\nBUDGET SUMMARY")
    print("=" * 60)

    for category, amount in result["breakdown"].items():
        print(
            f"{category.title():20}: "
            f"₹{amount:,.2f}"
        )

    print("-" * 60)

    print(
        f"Budget               : "
        f"₹{result['budget']:,.2f}"
    )

    print(
        f"Estimated Total      : "
        f"₹{result['estimated_total']:,.2f}"
    )

    print(
        f"Remaining Budget     : "
        f"₹{result['remaining_budget']:,.2f}"
    )

    print(
        f"Within Budget        : "
        f"{result['within_budget']}"
    )

    print("\nTRANSPORT CALCULATION")
    print("=" * 60)

    print(
        "Outbound: "
        "₹12,000 × 2 = ₹24,000"
    )

    print(
        "Return:   "
        "₹5,000 × 2 = ₹10,000"
    )

    print(
        "Transport Total: "
        "₹34,000"
    )

    print("\nVALIDATION")
    print("=" * 60)

    # ------------------------------------------
    # Expected transport
    # ------------------------------------------

    expected_outbound = 12000 * 2
    expected_return = 5000 * 2

    expected_transport = (
        expected_outbound
        + expected_return
    )

    # ------------------------------------------
    # Other costs
    # ------------------------------------------

    expected_accommodation = 16500
    expected_activity = 800 * 2
    expected_attraction = 0
    expected_restaurant = 1200 * 2

    expected_total = (
        expected_transport
        + expected_accommodation
        + expected_activity
        + expected_attraction
        + expected_restaurant
    )

    # ------------------------------------------
    # Assertions
    # ------------------------------------------

    assert (
        result["breakdown"]["transport"]
        == expected_transport
    )

    assert (
        result["breakdown"]["accommodation"]
        == expected_accommodation
    )

    assert (
        result["breakdown"]["activities"]
        == expected_activity
    )

    assert (
        result["breakdown"]["attractions"]
        == expected_attraction
    )

    assert (
        result["breakdown"]["restaurants"]
        == expected_restaurant
    )

    assert (
        result["estimated_total"]
        == expected_total
    )

    assert (
        result["remaining_budget"]
        == 50000 - expected_total
    )

    assert result["within_budget"] is False

    # ------------------------------------------
    # Validation output
    # ------------------------------------------

    print(
        "  ✓ Outbound transport cost calculated"
    )

    print(
        "  ✓ Return transport cost calculated"
    )

    print(
        "  ✓ Combined transport cost calculated"
    )

    print(
        "  ✓ Accommodation cost calculated"
    )

    print(
        "  ✓ Activity cost calculated"
    )

    print(
        "  ✓ Attraction cost calculated"
    )

    print(
        "  ✓ Restaurant cost calculated"
    )

    print(
        "  ✓ Total cost calculated"
    )

    print(
        "  ✓ Remaining budget calculated"
    )

    print(
        "  ✓ Budget status calculated"
    )

    print(
        "\n✅ Budget Calculator test passed."
    )


if __name__ == "__main__":
    main()