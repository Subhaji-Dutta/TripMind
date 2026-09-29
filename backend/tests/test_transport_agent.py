from backend.agents.transport_agent import TransportAgent
from backend.models.trip import TripRequest


def main():

    print("\nTesting TripMind Transport Agent")
    print("=" * 60)

    request = TripRequest(
        source="Delhi",
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-09-30",
        travelers=2,
        budget=50000,
        currency="INR",
    )

    agent = TransportAgent()

    outbound_options, return_options = agent.run(request)

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    print("\nOutbound options:")
    print("-" * 60)

    for option in outbound_options:
        print(
            f"  {option.mode} | "
            f"{option.provider} | "
            f"{option.departure} → {option.arrival} | "
            f"{option.duration} | "
            f"₹{option.estimated_cost:,.0f}"
        )

    print("\nReturn options:")
    print("-" * 60)

    for option in return_options:
        print(
            f"  {option.mode} | "
            f"{option.provider} | "
            f"{option.departure} → {option.arrival} | "
            f"{option.duration} | "
            f"₹{option.estimated_cost:,.0f}"
        )

    print("\n" + "=" * 60)
    print("TRANSPORT VALIDATION")
    print("=" * 60)

    assert len(outbound_options) == 3
    assert len(return_options) == 3

    print("  ✓ Exactly 3 outbound options returned")
    print("  ✓ Exactly 3 return options returned")

    for option in outbound_options:
        assert option.mode
        assert option.provider
        assert option.departure
        assert option.arrival
        assert option.duration
        assert option.estimated_cost >= 0

    for option in return_options:
        assert option.mode
        assert option.provider
        assert option.departure
        assert option.arrival
        assert option.duration
        assert option.estimated_cost >= 0

    print("  ✓ Outbound option fields are valid")
    print("  ✓ Return option fields are valid")

    outbound_modes = {
        option.mode.lower()
        for option in outbound_options
    }

    return_modes = {
        option.mode.lower()
        for option in return_options
    }

    assert len(outbound_modes) >= 2
    assert len(return_modes) >= 2

    print("  ✓ Multiple outbound transport modes provided")
    print("  ✓ Multiple return transport modes provided")

    print("\n" + "=" * 60)
    print("ROUTE VALIDATION")
    print("=" * 60)

    for option in outbound_options:
        assert "Delhi" in option.departure
        assert "Goa" in option.arrival

    for option in return_options:
        assert "Goa" in option.departure
        assert "Delhi" in option.arrival

    print("  ✓ Outbound route is Delhi → Goa")
    print("  ✓ Return route is Goa → Delhi")

    print("\n" + "=" * 60)
    print("API CALL VALIDATION")
    print("=" * 60)

    print("  ✓ One Transport Agent run generated both directions")

    print("\n✅ Transport Agent test passed.")


if __name__ == "__main__":
    main()