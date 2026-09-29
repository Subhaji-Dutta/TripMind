from backend.models.trip import TripRequest, TripPreferences


def main():

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
                "food",
                "nightlife"
            ],
            accommodation_type="comfortable",
            transport_preference="flight",
            food_preferences=[
                "seafood"
            ],
            travel_pace="balanced"
        )
    )

    print("\nTRIP REQUEST")
    print(request.model_dump_json(indent=2))


if __name__ == "__main__":
    main()