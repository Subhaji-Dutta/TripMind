from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Each agent family uses its own Groq key so that
    LLM usage is spread across the available accounts
    instead of hammering a single key.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # LLM routing (see backend.services.llm)
    groq_api_key: str  # fallback / general

    # Per-agent keys
    transport_agent_key: str
    accommodation_agent_key: str
    activity_agent_key: str
    attraction_agent_key: str
    restaurant_agent_key: str
    weather_agent_key: str
    packing_agent_key: str
    itinerary_agent_key: str


settings = Settings()