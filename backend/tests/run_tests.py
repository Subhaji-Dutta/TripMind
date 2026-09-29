import subprocess
import sys
import time


TESTS = [
    "backend.test_models",
    "backend.test_orchestrator",
    "backend.test_selection",
    "backend.test_transport_agent",
    "backend.test_weather_agent",
    "backend.test_accommodation_agent",
    "backend.test_restaurant_agent",
    "backend.test_recommendation_agent",
    "backend.test_packing_agent",
    "backend.test_itinerary_agent",
    "backend.test_budget",
]


# Small pause between tests so consecutive Groq requests
# are less likely to hit the organization's TPM limit.
DELAY_BETWEEN_TESTS = 3


def main():
    print("=" * 70)
    print("TRIPMIND TEST SUITE")
    print("=" * 70)

    passed = []
    failed = []

    for index, test_module in enumerate(TESTS):

        print("\n" + "-" * 70)
        print(f"Running: {test_module}")
        print("-" * 70)

        result = subprocess.run(
            [sys.executable, "-m", test_module]
        )

        if result.returncode == 0:
            passed.append(test_module)
        else:
            failed.append(test_module)

        if index < len(TESTS) - 1:
            print(
                f"\nWaiting {DELAY_BETWEEN_TESTS} seconds "
                "before the next test..."
            )
            time.sleep(DELAY_BETWEEN_TESTS)

    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)

    print(f"\nPassed: {len(passed)}")
    print(f"Failed: {len(failed)}")

    if passed:
        print("\nPASSED:")
        for test in passed:
            print(f"  ✓ {test}")

    if failed:
        print("\nFAILED:")
        for test in failed:
            print(f"  ✗ {test}")

    print()

    if failed:
        print("❌ TripMind test suite failed.")
        sys.exit(1)

    print("✅ All TripMind tests passed.")


if __name__ == "__main__":
    main()