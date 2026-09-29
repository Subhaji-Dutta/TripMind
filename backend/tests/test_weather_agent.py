from backend.agents.weather_agent import WeatherAgent
from backend.models.trip import TripRequest


def main():
    print("\nTesting TripMind Weather Agent")
    print("=" * 60)

    request = TripRequest(
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-09-30",
        travelers=2,
        budget=50000,
        currency="INR",
    )

    agent = WeatherAgent()
    result = agent.run(request)

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    print(f"Destination: {result.destination}")
    print(f"Forecast entries: {len(result.forecast)}")

    for day in result.forecast:
        print(
            f"  {day['date']} | "
            f"{day['temperature_c']}°C | "
            f"{day['condition']} | "
            f"Rain: {day['rain_probability']}%"
        )

    assert result.destination == "Goa"
    assert len(result.forecast) > 0

    # We expect one forecast entry for each requested date.
    assert len(result.forecast) == 4

    assert result.forecast[0]["date"] == "2026-09-27"
    assert result.forecast[-1]["date"] == "2026-09-30"

    print("\n✅ Weather Agent test passed.")


if __name__ == "__main__":
    main()