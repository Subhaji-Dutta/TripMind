import json
import os
from typing import List

from dotenv import load_dotenv
from groq import Groq

from backend.models.trip import (
    TripRequest,
    WeatherInfo,
    TransportOption,
    AccommodationOption,
    Restaurant,
    RecommendationResult,
    Activity,
    Attraction,
)


load_dotenv()


class RecommendationAgent:
    def __init__(self):
        api_key = os.getenv("RECOMMENDATION_AGENT_KEY")

        if not api_key:
            raise ValueError(
                "RECOMMENDATION_AGENT_KEY is not configured."
            )

        self.client = Groq(api_key=api_key)

    def run(
        self,
        request: TripRequest,
        weather: WeatherInfo,
        transport_options: List[TransportOption],
        accommodation_options: List[AccommodationOption],
        restaurants: List[Restaurant],
    ) -> RecommendationResult:

        print("  [REAL GROQ] Recommendation Agent called")

        restaurant_names = [
            restaurant.name
            for restaurant in restaurants
        ]

        prompt = f"""
You are the Recommendation Agent for TripMind.

Recommend activities, attractions, and restaurants
for this trip.

TRIP:
{request.model_dump_json(indent=2)}

WEATHER:
{weather.model_dump_json(indent=2)}

TRANSPORT OPTIONS:
{json.dumps(
    [option.model_dump() for option in transport_options],
    indent=2,
)}

ACCOMMODATION OPTIONS:
{json.dumps(
    [option.model_dump() for option in accommodation_options],
    indent=2,
)}

AVAILABLE RESTAURANTS:
{json.dumps(
    [restaurant.model_dump() for restaurant in restaurants],
    indent=2,
)}

IMPORTANT RESTAURANT RULE:

You MUST select restaurants ONLY from the
AVAILABLE RESTAURANTS list.

Available restaurant names are:

{json.dumps(restaurant_names, indent=2)}

DO NOT create, invent, rename, or modify restaurant names.

Return ONLY valid JSON in exactly this structure:

{{
  "activities": [
    {{
      "name": "string",
      "location": "string",
      "category": "string",
      "estimated_cost": 0,
      "duration": "string",
      "description": "string"
    }}
  ],
  "attractions": [
    {{
      "name": "string",
      "location": "string",
      "category": "string",
      "estimated_cost": 0,
      "duration": "string",
      "description": "string",
      "available_days": [],
      "opening_hours": "string"
    }}
  ],
  "restaurants": [
    {{
      "name": "EXACT NAME FROM AVAILABLE RESTAURANTS",
      "location": "string",
      "cuisine": "string",
      "price_range": "string",
      "estimated_cost": 0
    }}
  ]
}}

Rules:
- Return exactly 2 activities.
- Return exactly 2 attractions.
- Return exactly 2 restaurants.
- Restaurant names MUST exactly match names
  from AVAILABLE RESTAURANTS.
- Do not invent restaurant names.
- Do not create new restaurants.
- Use the actual destination.
- Consider the weather.
- Consider the user's interests.
- Consider the food preferences.
- Keep estimated costs numeric.
- Return JSON only.
- No markdown.
- No explanations.
"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise travel "
                        "recommendation engine. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=2500,
        )

        if not response.choices:
            raise ValueError(
                "Recommendation Agent received no choices from Groq."
            )

        choice = response.choices[0]
        content = choice.message.content

        if content is None or not content.strip():
            raise ValueError(
                "Recommendation Agent received an empty Groq response.\n"
                f"Finish reason: {choice.finish_reason}\n"
                f"Response: {response}"
            )

        content = content.strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Recommendation Agent returned invalid JSON.\n"
                f"Raw response:\n{content}"
            ) from exc

        activities_data = data.get("activities", [])
        attractions_data = data.get("attractions", [])
        restaurants_data = data.get("restaurants", [])

        if not isinstance(activities_data, list):
            raise ValueError(
                "Recommendation Agent returned an invalid "
                "'activities' list."
            )

        if not isinstance(attractions_data, list):
            raise ValueError(
                "Recommendation Agent returned an invalid "
                "'attractions' list."
            )

        if not isinstance(restaurants_data, list):
            raise ValueError(
                "Recommendation Agent returned an invalid "
                "'restaurants' list."
            )

        if len(activities_data) != 2:
            raise ValueError(
                "Recommendation Agent must return exactly "
                f"2 activities. Received: {len(activities_data)}"
            )

        if len(attractions_data) != 2:
            raise ValueError(
                "Recommendation Agent must return exactly "
                f"2 attractions. Received: {len(attractions_data)}"
            )

        if len(restaurants_data) != 2:
            raise ValueError(
                "Recommendation Agent must return exactly "
                f"2 restaurants. Received: {len(restaurants_data)}"
            )

        available_restaurants = {
            restaurant.name: restaurant
            for restaurant in restaurants
        }

        recommended_restaurants = []

        for item in restaurants_data:
            name = item.get("name")

            if name not in available_restaurants:
                raise ValueError(
                    "Recommendation Agent invented or modified "
                    f"a restaurant name: '{name}'. "
                    "Restaurant names must come from the "
                    "Restaurant Agent."
                )

            source_restaurant = available_restaurants[name]

            recommended_restaurants.append(
                Restaurant(
                    name=source_restaurant.name,
                    location=source_restaurant.location,
                    cuisine=source_restaurant.cuisine,
                    price_range=source_restaurant.price_range,
                    estimated_cost=source_restaurant.estimated_cost,
                )
            )

        return RecommendationResult(
            activities=[
                Activity(**activity)
                for activity in activities_data
            ],
            attractions=[
                Attraction(**attraction)
                for attraction in attractions_data
            ],
            restaurants=recommended_restaurants,
        )