import json
import os
from datetime import date, timedelta
from typing import Any, Dict

from dotenv import load_dotenv
from groq import Groq

from backend.models.trip import (
    TripRequest,
    WeatherInfo,
    SelectedTripOptions,
)

load_dotenv()


class ItineraryAgent:
    def __init__(self):
        api_key = os.getenv("ITINERARY_AGENT_KEY")

        if not api_key:
            raise ValueError(
                "ITINERARY_AGENT_KEY is not set in the environment."
            )

        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-20b"

    def run(
        self,
        request: TripRequest,
        weather: WeatherInfo,
        selected_options: SelectedTripOptions,
        packing_list,
    ) -> Dict[str, Any]:

        print("  [REAL GROQ] Itinerary Agent called")

        start = date.fromisoformat(request.start_date)
        end = date.fromisoformat(request.end_date)

        dates = []
        current = start

        while current <= end:
            dates.append(current.isoformat())
            current += timedelta(days=1)

        weather_json = json.dumps(
            weather.model_dump(),
            ensure_ascii=False,
        )

        selected_json = json.dumps(
            selected_options.model_dump(),
            ensure_ascii=False,
        )

        packing_json = json.dumps(
            packing_list,
            ensure_ascii=False,
        )

        prompt = f"""
Create a realistic day-by-day travel itinerary.

Return ONLY valid JSON.
Do not include markdown.
Do not explain your reasoning.

TRIP:
Destination: {request.destination}
Start date: {request.start_date}
End date: {request.end_date}
Travelers: {request.travelers}

DATES:
{json.dumps(dates)}

WEATHER:
{weather_json}

SELECTED OPTIONS:
{selected_json}

PACKING LIST:
{packing_json}

STRICT RULES:

1. Create exactly ONE day object for EVERY date in DATES.
2. Never create a day for a date outside DATES.
3. Use the selected activities, attractions, and restaurants.
4. DO NOT repeat the same activity on multiple days.
5. DO NOT repeat the same attraction on multiple days.
6. DO NOT repeat the same restaurant on multiple days.
7. If there are fewer selected activities than days, some days may have
   "No additional activity selected".
8. If there are fewer selected attractions than days, some days may have
   "No additional attraction selected".
9. If there are fewer selected restaurants than days, some days may have
   "No restaurant selected".
10. Never invent an activity, attraction, or restaurant that is not in
    SELECTED OPTIONS.
11. Consider weather when assigning outdoor activities and attractions.
12. On rainy or high-rain days, prefer indoor activities when available.
13. On clearer days, prefer outdoor attractions.
14. The itinerary must be practical and avoid impossible scheduling.
15. Use the exact names and locations from SELECTED OPTIONS.

IMPORTANT:
There may be fewer selected items than travel days.
Do NOT repeat an item just to fill a day.
It is better to leave a slot unused than to repeat an item.

Return exactly this structure:

{{
  "destination": "{request.destination}",
  "start_date": "{request.start_date}",
  "end_date": "{request.end_date}",
  "travelers": {request.travelers},
  "days": [
    {{
      "date": "YYYY-MM-DD",
      "weather": {{
        "temperature_c": 25.0,
        "condition": "Clear Sky",
        "rain_probability": 10
      }},
      "morning": {{
        "type": "activity",
        "name": "Selected activity or No additional activity selected",
        "location": "Location or empty string",
        "duration": "Duration or empty string"
      }},
      "afternoon": {{
        "type": "attraction",
        "name": "Selected attraction or No additional attraction selected",
        "location": "Location or empty string",
        "duration": "Duration or empty string"
      }},
      "evening": {{
        "type": "restaurant",
        "name": "Selected restaurant or No restaurant selected",
        "location": "Location or empty string",
        "cuisine": "Cuisine or empty string"
      }}
    }}
  ]
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return only valid JSON. "
                        "Do not explain reasoning. "
                        "Never repeat selected activities, attractions, "
                        "or restaurants."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=5000,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Itinerary Agent received an empty Groq response.\n"
                f"Finish reason: {response.choices[0].finish_reason}\n"
                f"Response: {response}"
            )

        try:
            itinerary = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Itinerary Agent returned invalid JSON:\n{content}"
            ) from exc

        if not isinstance(itinerary, dict):
            raise ValueError(
                "Itinerary Agent response must be a JSON object."
            )

        if "days" not in itinerary:
            raise ValueError(
                "Itinerary Agent response is missing 'days'."
            )

        if not isinstance(itinerary["days"], list):
            raise ValueError(
                "Itinerary Agent 'days' must be a list."
            )

        if len(itinerary["days"]) != len(dates):
            raise ValueError(
                f"Itinerary must contain exactly {len(dates)} days. "
                f"Received {len(itinerary['days'])}."
            )

        returned_dates = [
            day.get("date")
            for day in itinerary["days"]
        ]

        if returned_dates != dates:
            raise ValueError(
                "Itinerary dates do not match the requested trip dates."
            )

        # Validate that selected items are not repeated.
        selected_activity_names = {
            activity.name
            for activity in selected_options.activities
        }

        selected_attraction_names = {
            attraction.name
            for attraction in selected_options.attractions
        }

        selected_restaurant_names = {
            restaurant.name
            for restaurant in selected_options.restaurants
        }

        used_activities = []
        used_attractions = []
        used_restaurants = []

        for day in itinerary["days"]:
            morning = day.get("morning", {})
            afternoon = day.get("afternoon", {})
            evening = day.get("evening", {})

            activity_name = morning.get("name")
            attraction_name = afternoon.get("name")
            restaurant_name = evening.get("name")

            if activity_name in selected_activity_names:
                used_activities.append(activity_name)

            if attraction_name in selected_attraction_names:
                used_attractions.append(attraction_name)

            if restaurant_name in selected_restaurant_names:
                used_restaurants.append(restaurant_name)

        if len(used_activities) != len(set(used_activities)):
            raise ValueError(
                "Itinerary Agent repeated a selected activity."
            )

        if len(used_attractions) != len(set(used_attractions)):
            raise ValueError(
                "Itinerary Agent repeated a selected attraction."
            )

        if len(used_restaurants) != len(set(used_restaurants)):
            raise ValueError(
                "Itinerary Agent repeated a selected restaurant."
            )

        return itinerary


if __name__ == "__main__":
    print("Itinerary Agent module loaded successfully.")