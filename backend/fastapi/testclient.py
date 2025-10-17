from __future__ import annotations

import io
import json
from dataclasses import dataclass, is_dataclass
from typing import Any, Dict, Optional

from .applications import FastAPI
from .exceptions import HTTPException
from .uploads import UploadFile


@dataclass
class Response:
    status_code: int
    data: Any

    def json(self) -> Any:
        return self.data


class TestClient:
    def __init__(self, app: FastAPI):
        self.app = app

    def post(
        self,
        path: str,
        files: Optional[Dict[str, tuple[str, Any, Optional[str]]]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Response:
        request_data: Dict[str, Any] = {}
        if files:
            name, payload = next(iter(files.items()))
            filename, file_content, content_type = payload
            if isinstance(file_content, (bytes, bytearray)):
                buffer = io.BytesIO(file_content)
            else:
                buffer = file_content
            upload = UploadFile(filename=filename, file=buffer, content_type=content_type)
            request_data[name] = upload
        if json_body:
            request_data.update(json_body)
        try:
            result = self.app._call_route("POST", path, request_data)
            status_code = 200
        except HTTPException as exc:  # pragma: no cover - not expected in tests
            return Response(status_code=exc.status_code, data={"detail": exc.detail})
        return Response(status_code=status_code, data=_serialize(result))

    def get(self, path: str) -> Response:
        try:
            result = self.app._call_route("GET", path, {})
            status_code = 200
        except HTTPException as exc:  # pragma: no cover
            return Response(status_code=exc.status_code, data={"detail": exc.detail})
        return Response(status_code=status_code, data=_serialize(result))


def _serialize(data: Any) -> Any:
    if hasattr(data, "to_dict"):
        return data.to_dict()
    if hasattr(data, "model_dump"):
        return data.model_dump()
    if is_dataclass(data):
        from dataclasses import asdict
        return asdict(data)
    if isinstance(data, dict):
        return {key: _serialize(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_serialize(item) for item in data]
    return data
