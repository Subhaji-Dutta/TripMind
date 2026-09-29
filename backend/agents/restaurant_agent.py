import json
import os
from typing import List
from dotenv import load_dotenv
from groq import Groq

from backend.models.trip import Restaurant, TripRequest
load_dotenv()

class RestaurantAgent:
    def __init__(self):
        api_key = os.getenv("RESTAURANT_AGENT_KEY")

        if not api_key:
            raise ValueError(
                "RESTAURANT_AGENT_KEY is not set in the environment."
            )

        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-20b"

    def run(self, request: TripRequest) -> List[Restaurant]:
        print("  [REAL GROQ] Restaurant Agent called")

        prompt = f"""
Return ONLY valid JSON.

Create exactly 3 restaurant recommendations in {request.destination}.

Requirements:
- Exactly 3 restaurants.
- All must be in {request.destination}.
- Use 3 different restaurant names.
- Prefer real, well-known restaurants.
- Match these food preferences: {request.preferences.food_preferences}
- estimated_cost is a numeric amount in {request.currency} per person.
- Do not include explanations.
- Do not include markdown.
- Do not repeat any restaurant name.

Use exactly this JSON structure:

{{
  "restaurants": [
    {{
      "name": "Restaurant name",
      "location": "Location",
      "cuisine": "Cuisine",
      "price_range": "₹/₹₹/₹₹₹",
      "estimated_cost": 1000
    }},
    {{
      "name": "Restaurant name",
      "location": "Location",
      "cuisine": "Cuisine",
      "price_range": "₹/₹₹/₹₹₹",
      "estimated_cost": 1000
    }},
    {{
      "name": "Restaurant name",
      "location": "Location",
      "cuisine": "Cuisine",
      "price_range": "₹/₹₹/₹₹₹",
      "estimated_cost": 1000
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
                        "Return only the final JSON. "
                        "Do not explain your reasoning. "
                        "Do not repeat names."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            reasoning_effort="low",
            max_tokens=2000,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Restaurant Agent received an empty Groq response.\n"
                f"Finish reason: {response.choices[0].finish_reason}\n"
                f"Response: {response}"
            )

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Restaurant Agent returned invalid JSON:\n{content}"
            ) from exc

        restaurants_data = data.get("restaurants")

        if not isinstance(restaurants_data, list):
            raise ValueError(
                "Restaurant Agent response must contain a "
                "'restaurants' list."
            )

        if len(restaurants_data) != 3:
            raise ValueError(
                f"Restaurant Agent must return exactly 3 restaurants. "
                f"Received {len(restaurants_data)}."
            )

        restaurants = []

        for item in restaurants_data:
            restaurants.append(
                Restaurant(
                    name=item["name"],
                    location=item["location"],
                    cuisine=item.get("cuisine"),
                    price_range=item.get("price_range"),
                    estimated_cost=float(item.get("estimated_cost", 0)),
                )
            )

        names = [restaurant.name.strip().lower() for restaurant in restaurants]

        if len(set(names)) != 3:
            raise ValueError(
                "Restaurant Agent returned duplicate restaurant names."
            )

        return restaurants


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    request = TripRequest(
        destination="Goa",
        start_date="2026-09-27",
        end_date="2026-09-30",
        travelers=2,
        budget=50000,
        currency="INR",
        preferences={
            "interests": ["beaches", "nature", "food"],
            "accommodation_type": "comfortable",
            "transport_preference": "any",
            "food_preferences": ["Goan", "seafood"],
            "travel_pace": "balanced",
        },
    )

    agent = RestaurantAgent()
    restaurants = agent.run(request)

    print("\nRestaurant options:")
    for restaurant in restaurants:
        print(
            f"- {restaurant.name} | "
            f"{restaurant.location} | "
            f"{restaurant.cuisine} | "
            f"{restaurant.price_range} | "
            f"₹{restaurant.estimated_cost:,.0f}"
        )

    print("\nRestaurant Agent test passed.")