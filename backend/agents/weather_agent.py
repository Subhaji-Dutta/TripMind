from typing import List

import requests

from backend.models.trip import TripRequest, WeatherInfo


class WeatherAgent:
    """
    Weather Agent for TripMind.

    Uses:
    - Open-Meteo Geocoding API
    - Open-Meteo Forecast API

    No API key is required.
    """

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def run(self, request: TripRequest) -> WeatherInfo:
        print("  [REAL] Weather Agent called")

        latitude, longitude = self._get_coordinates(
            request.destination
        )

        forecast = self._get_forecast(
            latitude=latitude,
            longitude=longitude,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return WeatherInfo(
            destination=request.destination,
            forecast=forecast,
        )

    def _get_coordinates(
        self,
        destination: str,
    ) -> tuple[float, float]:

        response = requests.get(
            self.GEOCODING_URL,
            params={
    "name": destination,
    "count": 10,
    "language": "en",
    "format": "json",
    "countryCode": "IN",
},
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            raise ValueError(
                f"Could not find coordinates for "
                f"destination: {destination}"
            )

        location = results[0]

        return (
                float(location["latitude"]),
    float(location["longitude"]),
)

    def _get_forecast(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
    ) -> List[dict]:

        response = requests.get(
            self.FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
                "daily": (
                    "temperature_2m_max,"
                    "weather_code,"
                    "precipitation_probability_max"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        daily = data.get("daily")

        if not daily:
            raise ValueError(
                "Open-Meteo returned no daily forecast data."
            )

        forecast = []

        dates = daily.get("time", [])
        temperatures = daily.get(
            "temperature_2m_max", []
        )
        weather_codes = daily.get(
            "weather_code", []
        )
        rain_probabilities = daily.get(
            "precipitation_probability_max", []
        )

        for index, date_string in enumerate(dates):
            forecast.append(
                {
                    "date": date_string,
                    "temperature_c": temperatures[index],
                    "condition": self._weather_code_to_condition(
                        weather_codes[index]
                    ),
                    "weather_code": weather_codes[index],
                    "rain_probability": (
                        rain_probabilities[index]
                    ),
                }
            )

        return forecast

    @staticmethod
    def _weather_code_to_condition(
        weather_code: int,
    ) -> str:

        weather_conditions = {
            0: "Clear Sky",
            1: "Mainly Clear",
            2: "Partly Cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing Rime Fog",
            51: "Light Drizzle",
            53: "Moderate Drizzle",
            55: "Dense Drizzle",
            61: "Slight Rain",
            63: "Moderate Rain",
            65: "Heavy Rain",
            71: "Slight Snow",
            73: "Moderate Snow",
            75: "Heavy Snow",
            80: "Slight Rain Showers",
            81: "Moderate Rain Showers",
            82: "Violent Rain Showers",
            95: "Thunderstorm",
            96: "Thunderstorm with Slight Hail",
            99: "Thunderstorm with Heavy Hail",
        }

        return weather_conditions.get(
            weather_code,
            "Unknown",
        )