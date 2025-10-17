from __future__ import annotations

import io
from typing import BinaryIO, Optional


class UploadFile:
    def __init__(self, filename: str, file: BinaryIO, content_type: Optional[str] = None) -> None:
        self.filename = filename
        self.file = file
        self.content_type = content_type

    async def read(self) -> bytes:
        data = self.file.read()
        if isinstance(self.file, io.IOBase) and hasattr(self.file, "seek"):
            self.file.seek(0)
        return data
