from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    storage_path: Path = Path("./storage")
    model_name: str = "ollama/mistral"
    embedding_model: str = "local-similarity"
    max_workers: int = 2
    openai_base_url: str = "http://localhost:11434/v1"
    openai_api_key: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    storage_path = Path(os.getenv("PAPERHELPER_STORAGE_PATH", "./storage"))
    storage_path.mkdir(parents=True, exist_ok=True)
    return Settings(
        storage_path=storage_path,
        model_name=os.getenv("PAPERHELPER_MODEL_NAME", "ollama/mistral"),
        embedding_model=os.getenv("PAPERHELPER_EMBEDDING_MODEL", "local-similarity"),
        max_workers=int(os.getenv("PAPERHELPER_MAX_WORKERS", "2")),
        openai_base_url=os.getenv("PAPERHELPER_OPENAI_BASE_URL", "http://localhost:11434/v1"),
        openai_api_key=os.getenv("PAPERHELPER_OPENAI_API_KEY"),
    )
