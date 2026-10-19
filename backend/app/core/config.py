"""
WebMender AI — Core Configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "WebMender AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # TinyFish API
    TINYFISH_API_KEY: str = ""
    TINYFISH_BROWSER_ENDPOINT: str = "https://browser.tinyfish.ai"
    TINYFISH_AGENT_ENDPOINT: str = "https://agent.tinyfish.ai/v1/automation/run-sse"
    TINYFISH_SEARCH_ENDPOINT: str = "https://api.tinyfish.ai/v1/search"
    TINYFISH_FETCH_ENDPOINT: str = "https://api.tinyfish.ai/v1/fetch"

    # LLM
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.2

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Repair Settings
    MAX_REPAIR_RETRIES: int = 3
    REPAIR_TIMEOUT_SECONDS: int = 60
    SCREENSHOT_DIFF_THRESHOLD: float = 0.15

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
