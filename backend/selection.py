from typing import List

from backend.models.trip import (
    TripState,
    TransportOption,
    AccommodationOption,
    Activity,
    Attraction,
    Restaurant,
    SelectedTripOptions,
)


class TripSelection:

    @staticmethod
    def _transport_matches(
        selected: TransportOption,
        available: List[TransportOption],
    ) -> bool:
        return any(
            selected == option
            for option in available
        )

    @staticmethod
    def _accommodation_matches(
        selected: AccommodationOption,
        available: List[AccommodationOption],
    ) -> bool:
        return any(
            selected == option
            for option in available
        )

    @staticmethod
    def _activity_matches(
        selected: Activity,
        available: List[Activity],
    ) -> bool:
        return any(
            selected == option
            for option in available
        )

    @staticmethod
    def _attraction_matches(
        selected: Attraction,
        available: List[Attraction],
    ) -> bool:
        return any(
            selected == option
            for option in available
        )

    @staticmethod
    def _restaurant_matches(
        selected: Restaurant,
        available: List[Restaurant],
    ) -> bool:
        return any(
            selected == option
            for option in available
        )

    @staticmethod
    def apply_selection(
        state: TripState,
        outbound_transport: TransportOption,
        return_transport: TransportOption,
        accommodation: AccommodationOption,
        activities: List[Activity],
        attractions: List[Attraction],
        restaurants: List[Restaurant],
    ) -> TripState:

        if state.recommendations is None:
            raise ValueError(
                "Recommendations must exist before selecting options."
            )

        # Validate outbound transport
        if not TripSelection._transport_matches(
            outbound_transport,
            state.outbound_transport_options,
        ):
            raise ValueError(
                "Selected outbound transport is not one "
                "of the available outbound options."
            )

        # Validate return transport
        if not TripSelection._transport_matches(
            return_transport,
            state.return_transport_options,
        ):
            raise ValueError(
                "Selected return transport is not one "
                "of the available return options."
            )

        # Validate accommodation
        if not TripSelection._accommodation_matches(
            accommodation,
            state.accommodation_options,
        ):
            raise ValueError(
                "Selected accommodation is not one "
                "of the available accommodation options."
            )

        # Validate activities
        for activity in activities:
            if not TripSelection._activity_matches(
                activity,
                state.recommendations.activities,
            ):
                raise ValueError(
                    f"Selected activity '{activity.name}' "
                    "is not one of the recommendations."
                )

        # Validate attractions
        for attraction in attractions:
            if not TripSelection._attraction_matches(
                attraction,
                state.recommendations.attractions,
            ):
                raise ValueError(
                    f"Selected attraction '{attraction.name}' "
                    "is not one of the recommendations."
                )

        # Validate restaurants
        for restaurant in restaurants:
            if not TripSelection._restaurant_matches(
                restaurant,
                state.recommendations.restaurants,
            ):
                raise ValueError(
                    f"Selected restaurant '{restaurant.name}' "
                    "is not one of the recommendations."
                )

        state.selected_options = SelectedTripOptions(
            outbound_transport=outbound_transport,
            return_transport=return_transport,
            accommodation=accommodation,
            activities=activities,
            attractions=attractions,
            restaurants=restaurants,
            )

        return state