from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field


class TripPreferences(BaseModel):
    interests: List[str] = Field(default_factory=list)
    accommodation_type: str = "comfortable"
    transport_preference: str = "any"
    food_preferences: List[str] = Field(default_factory=list)
    travel_pace: str = "balanced"


class TripRequest(BaseModel):
    source: str
    destination: str
    start_date: str
    end_date: str
    travelers: int = 1
    budget: float
    currency: str = "INR"
    preferences: TripPreferences = Field(
        default_factory=TripPreferences
    )


class TransportOption(BaseModel):
    mode: str
    provider: Optional[str] = None
    departure: Optional[str] = None
    arrival: Optional[str] = None
    duration: Optional[str] = None
    estimated_cost: float = 0


class AccommodationOption(BaseModel):
    name: str
    location: str
    rating: Optional[float] = None
    price_per_night: float = 0
    total_cost: float = 0
    amenities: List[str] = Field(default_factory=list)


class Activity(BaseModel):
    name: str
    location: str
    category: str
    estimated_cost: float = 0
    duration: Optional[str] = None
    description: Optional[str] = None


class Attraction(BaseModel):
    name: str
    location: str
    category: str
    estimated_cost: float = 0
    duration: Optional[str] = None
    description: Optional[str] = None
    available_days: List[str] = Field(default_factory=list)
    opening_hours: Optional[str] = None


class Restaurant(BaseModel):
    name: str
    location: str
    cuisine: Optional[str] = None
    price_range: Optional[str] = None
    estimated_cost: float = 0


class WeatherInfo(BaseModel):
    destination: str
    forecast: List[Dict[str, Any]] = Field(default_factory=list)


class RecommendationResult(BaseModel):
    activities: List[Activity] = Field(default_factory=list)
    attractions: List[Attraction] = Field(default_factory=list)
    restaurants: List[Restaurant] = Field(default_factory=list)


class SelectedTripOptions(BaseModel):
    outbound_transport:Optional[TransportOption] = None
    return_transport: Optional[TransportOption] = None
    accommodation: Optional[AccommodationOption] = None
    activities: List[Activity] = Field(default_factory=list)
    attractions: List[Attraction] = Field(default_factory=list)
    restaurants: List[Restaurant] = Field(default_factory=list)


class TripState(BaseModel):
    request: TripRequest
    weather: Optional[WeatherInfo] = None
    outbound_transport_options: List[TransportOption] = Field(
    default_factory=list
    )
    return_transport_options: List[TransportOption] = Field(
    default_factory=list
    )
    accommodation_options: List[AccommodationOption] = Field(
        default_factory=list
    )
    restaurants: List[Restaurant] = Field(default_factory=list)
    recommendations: Optional[RecommendationResult] = None
    selected_options: Optional[SelectedTripOptions] = None
    packing_list: List[str] = Field(default_factory=list)
    final_itinerary: Optional[Dict[str, Any]] = None
    budget_summary: Optional[Dict[str, Any]] = None


class TripSelectionRequest(BaseModel):
    trip_id: str
    outbound_transport: TransportOption
    return_transport: TransportOption
    accommodation: AccommodationOption
    activities: List[Activity] = Field(default_factory=list)
    attractions: List[Attraction] = Field(default_factory=list)
    restaurants: List[Restaurant] = Field(default_factory=list)