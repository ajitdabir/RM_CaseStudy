from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str | None
    openai_model: str
    gemini_api_key: str | None
    gemini_model: str
    default_provider: str
    app_title: str
    app_brand: str


def get_config() -> AppConfig:
    return AppConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        default_provider=os.getenv("DEFAULT_PROVIDER", "OpenAI"),
        app_title=os.getenv("APP_TITLE", "RM Capability Engine"),
        app_brand=os.getenv("APP_BRAND", "scripbox"),
    )