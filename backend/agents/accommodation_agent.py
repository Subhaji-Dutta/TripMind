import json
import os
from datetime import date
from typing import List

from dotenv import load_dotenv
from groq import Groq

from backend.models.trip import TripRequest, AccommodationOption


load_dotenv()


class AccommodationAgent:
    def __init__(self):
        api_key = os.getenv("ACCOMMODATION_AGENT_KEY")

        if not api_key:
            raise ValueError(
                "ACCOMMODATION_AGENT_KEY is not configured."
            )

        self.client = Groq(api_key=api_key)

    def run(
        self,
        request: TripRequest,
    ) -> List[AccommodationOption]:

        print("  [REAL GROQ] Accommodation Agent called")

        start = date.fromisoformat(request.start_date)
        end = date.fromisoformat(request.end_date)

        nights = (end - start).days

        if nights <= 0:
            raise ValueError(
                "End date must be after start date."
            )

        prompt = f"""
You are the Accommodation Agent for TripMind,
an AI travel planner.

Suggest exactly 2 suitable accommodation options
for this trip.

TRIP:
{request.model_dump_json(indent=2)}

NUMBER OF NIGHTS:
{nights}

Important:
These are AI-generated planning recommendations,
not live hotel availability or confirmed prices.

Return ONLY valid JSON in this exact structure:

{{
  "accommodations": [
    {{
      "name": "string",
      "location": "string",
      "rating": 4.0,
      "price_per_night": 3000,
      "amenities": [
        "Wi-Fi",
        "Breakfast"
      ]
    }}
  ]
}}

Rules:
- Return exactly 2 accommodations.
- Use the requested destination.
- Consider the total trip budget.
- Consider the requested accommodation type.
- Keep price_per_night numeric.
- Keep rating numeric between 1 and 5.
- Give realistic estimated prices in {request.currency}.
- Do not claim live availability.
- Do not claim the price is currently bookable.
- Return JSON only.
"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a travel accommodation "
                        "recommendation engine. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Accommodation Agent received an empty Groq response."
            )

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Accommodation Agent returned invalid JSON: {content}"
            ) from exc

        accommodations = []

        for item in data.get("accommodations", []):
            price_per_night = float(
                item["price_per_night"]
            )

            accommodations.append(
                AccommodationOption(
                    name=item["name"],
                    location=item["location"],
                    rating=float(item["rating"]),
                    price_per_night=price_per_night,
                    total_cost=price_per_night * nights,
                    amenities=item.get(
                        "amenities",
                        [],
                    ),
                )
            )

        return accommodations