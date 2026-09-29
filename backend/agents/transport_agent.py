import json
import os
from typing import List, Tuple

from dotenv import load_dotenv
from groq import Groq

from backend.models.trip import TripRequest, TransportOption


load_dotenv()


class TransportAgent:
    def __init__(self):
        api_key = os.getenv("TRANSPORT_AGENT_KEY")

        if not api_key:
            raise ValueError(
                "TRANSPORT_AGENT_KEY is not configured."
            )

        self.client = Groq(api_key=api_key)

    def run(
        self,
        request: TripRequest,
    ) -> Tuple[List[TransportOption], List[TransportOption]]:

        print("  [REAL GROQ] Transport Agent called")

        prompt = f"""
You are the Transport Agent for TripMind,
an AI travel planner.

Generate transport options for BOTH directions
of the following round trip.

TRIP REQUEST:

{request.model_dump_json(indent=2)}

The outbound journey is:

{request.source} → {request.destination}

The return journey is:

{request.destination} → {request.source}

Return ONLY valid JSON in exactly this structure:

{{
  "outbound_options": [
    {{
      "mode": "Flight",
      "provider": "string",
      "departure": "string",
      "arrival": "string",
      "duration": "string",
      "estimated_cost": 0
    }}
  ],
  "return_options": [
    {{
      "mode": "Flight",
      "provider": "string",
      "departure": "string",
      "arrival": "string",
      "duration": "string",
      "estimated_cost": 0
    }}
  ]
}}

Rules:

- Return exactly 3 outbound options.
- Return exactly 3 return options.
- Use the actual source and destination from the TRIP REQUEST.
- Outbound options must travel from source to destination.
- Return options must travel from destination back to source.
- Consider multiple transport modes where practical,
  such as Flight, Train, Bus, or Car.
- Consider the traveler's transport preference.
- Consider the total trip budget.
- estimated_cost must be numeric.
- estimated_cost is an AI-generated estimate,
  NOT a live price.
- Departure and arrival should be locations,
  not exact airport/train station codes unless known.
- Do not claim live availability.
- Do not claim that tickets are currently bookable.
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
                        "You are a precise transport "
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
            max_tokens=3000,
        )

        if not response.choices:
            raise ValueError(
                "Transport Agent received no choices from Groq."
            )

        choice = response.choices[0]
        content = choice.message.content

        if content is None or not content.strip():
            raise ValueError(
                "Transport Agent received an empty Groq response.\n"
                f"Finish reason: {choice.finish_reason}\n"
                f"Response: {response}"
            )

        content = content.strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Transport Agent returned invalid JSON.\n"
                f"Raw response:\n{content}"
            ) from exc

        outbound_data = data.get("outbound_options")
        return_data = data.get("return_options")

        if not isinstance(outbound_data, list):
            raise ValueError(
                "Transport Agent response does not contain "
                "a valid 'outbound_options' list."
            )

        if not isinstance(return_data, list):
            raise ValueError(
                "Transport Agent response does not contain "
                "a valid 'return_options' list."
            )

        if len(outbound_data) != 3:
            raise ValueError(
                "Transport Agent must return exactly "
                "3 outbound options. "
                f"Received: {len(outbound_data)}"
            )

        if len(return_data) != 3:
            raise ValueError(
                "Transport Agent must return exactly "
                "3 return options. "
                f"Received: {len(return_data)}"
            )

        def build_options(items):
            options = []

            for item in items:
                options.append(
                    TransportOption(
                        mode=item["mode"],
                        provider=item.get("provider"),
                        departure=item.get("departure"),
                        arrival=item.get("arrival"),
                        duration=item.get("duration"),
                        estimated_cost=float(
                            item["estimated_cost"]
                        ),
                    )
                )

            return options

        outbound_options = build_options(outbound_data)
        return_options = build_options(return_data)

        return outbound_options, return_options