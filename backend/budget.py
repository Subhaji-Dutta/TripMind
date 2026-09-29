from backend.models.trip import TripState


class BudgetCalculator:

    @staticmethod
    def calculate(state: TripState) -> dict:
        if state.selected_options is None:
            raise ValueError(
                "Cannot calculate budget before trip options are selected."
            )

        selected = state.selected_options
        request = state.request

        transport_cost = 0.0
        accommodation_cost = 0.0
        activity_cost = 0.0
        attraction_cost = 0.0
        restaurant_cost = 0.0

        if selected.outbound_transport is not None:
            transport_cost += (
            selected.outbound_transport.estimated_cost
            * request.travelers
            )

        if selected.return_transport is not None:
            transport_cost += (
            selected.return_transport.estimated_cost
            * request.travelers
            )

        if selected.accommodation is not None:
            accommodation_cost = (
                selected.accommodation.total_cost
            )

        activity_cost = sum(
            activity.estimated_cost * request.travelers
            for activity in selected.activities
        )

        attraction_cost = sum(
            attraction.estimated_cost * request.travelers
            for attraction in selected.attractions
        )

        restaurant_cost = sum(
            restaurant.estimated_cost * request.travelers
            for restaurant in selected.restaurants
        )

        estimated_total = (
            transport_cost
            + accommodation_cost
            + activity_cost
            + attraction_cost
            + restaurant_cost
        )

        remaining_budget = request.budget - estimated_total

        return {
            "currency": request.currency,
            "budget": request.budget,
            "breakdown": {
                "transport": transport_cost,
                "accommodation": accommodation_cost,
                "activities": activity_cost,
                "attractions": attraction_cost,
                "restaurants": restaurant_cost,
            },
            "estimated_total": estimated_total,
            "remaining_budget": remaining_budget,
            "within_budget": remaining_budget >= 0,
        }