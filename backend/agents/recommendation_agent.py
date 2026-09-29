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
    ) -> RecommendationResult:

        print("  [REAL GROQ] Recommendation Agent called")

        prompt = f"""
You are the Recommendation Agent for TripMind.

Your responsibility is ONLY to generate candidate
activities and attractions for the trip.

Restaurant recommendations are handled separately by
the Restaurant Agent.

DO NOT generate restaurants.
DO NOT include restaurants in your response.

The next stage is a deterministic Python Planning Engine.
The Planning Engine will compare your activities and
attractions against the trip budget, duration, weather,
transport, accommodation, and restaurant options.

Therefore, provide a useful candidate pool rather than
trying to create the final trip plan.

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
  ]
}}

Rules:

- Return exactly 3 activities.
- Return exactly 3 attractions.
- Do NOT return restaurants.
- Do NOT create a restaurants field.
- Use the actual destination.
- Consider the weather.
- Consider the user's interests.
- Consider the user's travel pace.
- Include a variety of categories.
- Include a mixture of low-cost and higher-cost options
  where appropriate.
- Keep estimated_cost numeric.
- Do not use negative costs.
- Keep descriptions concise.
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
                        "Your responsibility is to "
                        "generate activity and attraction "
                        "candidates only. "
                        "Restaurants are handled by a "
                        "separate agent. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=3500,
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

        if "restaurants" in data:
            raise ValueError(
                "Recommendation Agent must not return restaurants. "
                "Restaurants are handled by Restaurant Agent."
            )

        if len(activities_data) != 3:
            raise ValueError(
                "Recommendation Agent must return exactly "
                f"3 activities. Received: {len(activities_data)}"
            )

        if len(attractions_data) != 3:
            raise ValueError(
                "Recommendation Agent must return exactly "
                f"3 attractions. Received: {len(attractions_data)}"
            )

        activities = []

        for activity in activities_data:
            cost = activity.get("estimated_cost", 0)

            if not isinstance(cost, (int, float)):
                raise ValueError(
                    "Activity estimated_cost must be numeric."
                )

            if cost < 0:
                raise ValueError(
                    "Activity estimated_cost cannot be negative."
                )

            activities.append(
                Activity(**activity)
            )

        attractions = []

        for attraction in attractions_data:
            cost = attraction.get("estimated_cost", 0)

            if not isinstance(cost, (int, float)):
                raise ValueError(
                    "Attraction estimated_cost must be numeric."
                )

            if cost < 0:
                raise ValueError(
                    "Attraction estimated_cost cannot be negative."
                )

            attractions.append(
                Attraction(**attraction)
            )

        return RecommendationResult(
            activities=activities,
            attractions=attractions,
        )