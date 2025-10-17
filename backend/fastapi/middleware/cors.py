from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class CORSMiddleware:
    app: object
    allow_origins: Iterable[str] | None = None
    allow_credentials: bool = False
    allow_methods: Iterable[str] | None = None
    allow_headers: Iterable[str] | None = None
