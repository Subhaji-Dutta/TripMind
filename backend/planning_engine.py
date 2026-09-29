from datetime import date, timedelta
from typing import List, Tuple

from backend.models.trip import (
    Activity,
    Attraction,
    PlannedDay,
    PlanningOption,
    PlanningResult,
    Restaurant,
    TripState,
)


class PlanningEngine:
    """
    Deterministic planning engine.

    Uses only data already collected by the agents and stored in TripState.

    It does NOT:
    - call an LLM
    - call any agent
    - call an external API

    Therefore the engine can safely be executed repeatedly after
    user changes without regenerating agent data.
    """

    MAX_OPTIONS = 6
    MAX_ACTIVITIES_PER_DAY = 2
    MAX_ATTRACTIONS_PER_DAY = 2
    MAX_DAILY_HOURS = 8

    @staticmethod
    def _trip_dates(state: TripState) -> List[date]:
        start = date.fromisoformat(state.request.start_date)
        end = date.fromisoformat(state.request.end_date)

        if end < start:
            raise ValueError("End date cannot be before start date.")

        dates = []
        current = start

        while current <= end:
            dates.append(current)
            current += timedelta(days=1)

        return dates

    @staticmethod
    def _duration_hours(duration: str | None) -> float:
        if not duration:
            return 2.0

        text = duration.lower().strip()

        try:
            parts = text.split()

            if "hour" in text or "hr" in text:
                return float(parts[0])

            if "minute" in text or "min" in text:
                return float(parts[0]) / 60

        except (ValueError, IndexError):
            pass

        return 2.0

    @staticmethod
    def _activity_cost(
        activity: Activity,
        travelers: int,
    ) -> float:
        return activity.estimated_cost * travelers

    @staticmethod
    def _attraction_cost(
        attraction: Attraction,
        travelers: int,
    ) -> float:
        return attraction.estimated_cost * travelers

    @staticmethod
    def _restaurant_cost(
        restaurant: Restaurant,
        travelers: int,
    ) -> float:
        return restaurant.estimated_cost * travelers

    @staticmethod
    def _transport_cost(
        state: TripState,
        outbound,
        return_transport,
    ) -> float:
        travelers = state.request.travelers

        outbound_cost = (
            outbound.estimated_cost * travelers
            if outbound
            else 0
        )

        return_cost = (
            return_transport.estimated_cost * travelers
            if return_transport
            else 0
        )

        return outbound_cost + return_cost

    @staticmethod
    def _accommodation_cost(accommodation) -> float:
        if accommodation is None:
            return 0

        return accommodation.total_cost

    @staticmethod
    def _rotate_items(items, offset: int):
        if not items:
            return []

        offset = offset % len(items)

        return items[offset:] + items[:offset]

    def _build_daily_plan(
        self,
        state: TripState,
        activities: List[Activity],
        attractions: List[Attraction],
        restaurants: List[Restaurant],
    ) -> List[PlannedDay]:

        dates = self._trip_dates(state)
        travelers = state.request.travelers

        daily_plans = [
            PlannedDay(date=trip_date.isoformat())
            for trip_date in dates
        ]

        activity_index = 0
        attraction_index = 0
        restaurant_index = 0

        for day in daily_plans:
            daily_hours = 0.0

            # ---------------------------------
            # Add activities
            # ---------------------------------
            while (
                activity_index < len(activities)
                and len(day.activities)
                < self.MAX_ACTIVITIES_PER_DAY
            ):
                activity = activities[activity_index]
                duration = self._duration_hours(activity.duration)

                if daily_hours + duration > self.MAX_DAILY_HOURS:
                    break

                day.activities.append(activity)
                daily_hours += duration
                activity_index += 1

            # ---------------------------------
            # Add attractions
            # ---------------------------------
            while (
                attraction_index < len(attractions)
                and len(day.attractions)
                < self.MAX_ATTRACTIONS_PER_DAY
            ):
                attraction = attractions[attraction_index]
                duration = self._duration_hours(attraction.duration)

                if daily_hours + duration > self.MAX_DAILY_HOURS:
                    break

                day.attractions.append(attraction)
                daily_hours += duration
                attraction_index += 1

            # ---------------------------------
            # Add one restaurant per day
            # ---------------------------------
            if restaurant_index < len(restaurants):
                day.restaurants.append(
                    restaurants[restaurant_index]
                )
                restaurant_index += 1

            # ---------------------------------
            # Calculate daily cost
            # ---------------------------------
            activity_cost = sum(
                self._activity_cost(activity, travelers)
                for activity in day.activities
            )

            attraction_cost = sum(
                self._attraction_cost(attraction, travelers)
                for attraction in day.attractions
            )

            restaurant_cost = sum(
                self._restaurant_cost(restaurant, travelers)
                for restaurant in day.restaurants
            )

            day.estimated_cost = (
                activity_cost
                + attraction_cost
                + restaurant_cost
            )

        return daily_plans

    def _calculate_total(
        self,
        state: TripState,
        outbound,
        return_transport,
        accommodation,
        daily_plan: List[PlannedDay],
    ) -> float:

        transport_cost = self._transport_cost(
            state,
            outbound,
            return_transport,
        )

        accommodation_cost = self._accommodation_cost(
            accommodation
        )

        daily_cost = sum(
            day.estimated_cost
            for day in daily_plan
        )

        return (
            transport_cost
            + accommodation_cost
            + daily_cost
        )

    @staticmethod
    def _option_key(
        outbound,
        return_transport,
        accommodation,
        activities,
        attractions,
        restaurants,
    ) -> Tuple:

        return (
            outbound.mode if outbound else None,
            outbound.provider if outbound else None,
            outbound.estimated_cost if outbound else None,
            return_transport.mode if return_transport else None,
            return_transport.provider
            if return_transport
            else None,
            return_transport.estimated_cost
            if return_transport
            else None,
            accommodation.name
            if accommodation
            else None,
            tuple(activity.name for activity in activities),
            tuple(attraction.name for attraction in attractions),
            tuple(restaurant.name for restaurant in restaurants),
        )

    def _create_candidate(
        self,
        state: TripState,
        outbound,
        return_transport,
        accommodation,
        activities,
        attractions,
        restaurants,
        variant_number: int,
    ) -> PlanningOption:

        daily_plan = self._build_daily_plan(
            state=state,
            activities=activities,
            attractions=attractions,
            restaurants=restaurants,
        )

        # Collect only items actually used in the daily schedule.
        planned_activities = []
        planned_attractions = []
        planned_restaurants = []

        for day in daily_plan:
            planned_activities.extend(day.activities)
            planned_attractions.extend(day.attractions)
            planned_restaurants.extend(day.restaurants)

        estimated_total = self._calculate_total(
            state=state,
            outbound=outbound,
            return_transport=return_transport,
            accommodation=accommodation,
            daily_plan=daily_plan,
        )

        remaining_budget = state.request.budget - estimated_total

        return PlanningOption(
            name=(
                f"Plan {variant_number}: "
                f"{outbound.mode} + {accommodation.name}"
            ),
            description=(
                "Alternative trip plan generated from the "
                "cached trip data."
            ),
            outbound_transport=outbound,
            return_transport=return_transport,
            accommodation=accommodation,
            activities=planned_activities,
            attractions=planned_attractions,
            restaurants=planned_restaurants,
            daily_plan=daily_plan,
            estimated_total=estimated_total,
            remaining_budget=remaining_budget,
            within_budget=remaining_budget >= 0,
        )

    def run(self, state: TripState) -> PlanningResult:

        # ---------------------------------
        # Validate cached agent data
        # ---------------------------------
        if not state.outbound_transport_options:
            raise ValueError(
                "No outbound transport options available."
            )

        if not state.return_transport_options:
            raise ValueError(
                "No return transport options available."
            )

        if not state.accommodation_options:
            raise ValueError(
                "No accommodation options available."
            )

        if state.recommendations is None:
            raise ValueError(
                "No recommendation data available."
            )

        # ---------------------------------
        # Read ONLY cached agent data
        # ---------------------------------
        base_activities = list(
            state.recommendations.activities
        )

        base_attractions = list(
            state.recommendations.attractions
        )

        base_restaurants = list(
            state.restaurants
        )

        candidates: List[PlanningOption] = []
        seen = set()

        # ---------------------------------
        # Generate deterministic alternatives
        # ---------------------------------
        variant_number = 1

        for outbound_index, outbound in enumerate(
            state.outbound_transport_options
        ):

            for return_index, return_transport in enumerate(
                state.return_transport_options
            ):

                for accommodation_index, accommodation in enumerate(
                    state.accommodation_options
                ):

                    if variant_number > self.MAX_OPTIONS:
                        break

                    activity_offset = (
                        outbound_index
                        + accommodation_index
                    ) % max(len(base_activities), 1)

                    attraction_offset = (
                        return_index
                        + accommodation_index
                    ) % max(len(base_attractions), 1)

                    restaurant_offset = (
                        outbound_index
                        + return_index
                    ) % max(len(base_restaurants), 1)

                    activities = self._rotate_items(
                        base_activities,
                        activity_offset,
                    )

                    attractions = self._rotate_items(
                        base_attractions,
                        attraction_offset,
                    )

                    restaurants = self._rotate_items(
                        base_restaurants,
                        restaurant_offset,
                    )

                    key = self._option_key(
                        outbound,
                        return_transport,
                        accommodation,
                        activities,
                        attractions,
                        restaurants,
                    )

                    if key in seen:
                        continue

                    seen.add(key)

                    candidate = self._create_candidate(
                        state=state,
                        outbound=outbound,
                        return_transport=return_transport,
                        accommodation=accommodation,
                        activities=activities,
                        attractions=attractions,
                        restaurants=restaurants,
                        variant_number=variant_number,
                    )

                    # Only feasible plans are returned.
                    if candidate.within_budget:
                        candidates.append(candidate)
                        variant_number += 1

                if variant_number > self.MAX_OPTIONS:
                    break

            if variant_number > self.MAX_OPTIONS:
                break

        if not candidates:
            raise ValueError(
                "No feasible planning options are within the trip budget."
            )

        return PlanningResult(
            options=candidates
        )