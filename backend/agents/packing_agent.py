import json
import os
from typing import List

from dotenv import load_dotenv
from groq import Groq

from backend.models.trip import (
    TripRequest,
    WeatherInfo,
    SelectedTripOptions,
)


load_dotenv()


class PackingAgent:
    def __init__(self):
        api_key = os.getenv("PACKING_AGENT_KEY")

        if not api_key:
            raise ValueError(
                "PACKING_AGENT_KEY is not configured."
            )

        self.client = Groq(api_key=api_key)

    def run(
        self,
        request: TripRequest,
        weather: WeatherInfo,
        selected_options: SelectedTripOptions,
    ) -> List[str]:

        print("  [REAL GROQ] Packing Agent called")

        prompt = f"""
You are the Packing Agent for TripMind,
an AI travel planner.

Create a personalized packing list based on the
traveler's trip, weather, and selected activities.

TRIP REQUEST:
{request.model_dump_json(indent=2)}

WEATHER:
{weather.model_dump_json(indent=2)}

SELECTED TRANSPORT:
{json.dumps(
    {
    "outbound_transport": (
        selected_options.outbound_transport.model_dump()
        if selected_options.outbound_transport
        else None
    ),
    "return_transport": (
        selected_options.return_transport.model_dump()
        if selected_options.return_transport
        else None
    ),
}
    if selected_options.outbound_transport or selected_options.restaurants
    else None,
    indent=2
)}

SELECTED ACCOMMODATION:
{json.dumps(
    selected_options.accommodation.model_dump()
    if selected_options.accommodation
    else None,
    indent=2
)}

SELECTED ACTIVITIES:
{json.dumps(
    [item.model_dump() for item in selected_options.activities],
    indent=2
)}

SELECTED ATTRACTIONS:
{json.dumps(
    [item.model_dump() for item in selected_options.attractions],
    indent=2
)}

SELECTED RESTAURANTS:
{json.dumps(
    [item.model_dump() for item in selected_options.restaurants],
    indent=2
)}

Return ONLY valid JSON in exactly this structure:

{{
  "packing_list": [
    "item 1",
    "item 2",
    "item 3"
  ]
}}

Rules:
- Create a practical packing list.
- Consider every day's weather.
- Consider rain probability.
- Consider temperature.
- Consider selected activities.
- Consider selected attractions.
- Consider the transport mode.
- Include essential travel items.
- Avoid unnecessary duplicate items.
- Do not include explanations outside the JSON.
- Return between 8 and 20 useful items.
"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a practical travel packing "
                        "assistant. Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
            max_tokens=1200,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Packing Agent received an empty Groq response."
            )

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Packing Agent returned invalid JSON: {content}"
            ) from exc

        packing_list = data.get("packing_list", [])

        if not isinstance(packing_list, list):
            raise ValueError(
                "Packing Agent returned an invalid packing_list."
            )

        packing_list = [
            str(item).strip()
            for item in packing_list
            if str(item).strip()
        ]

        if not packing_list:
            raise ValueError(
                "Packing Agent returned an empty packing list."
            )

        return list(dict.fromkeys(packing_list))