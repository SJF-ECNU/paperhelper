from __future__ import annotations

import asyncio
from typing import Any, Callable, List, Tuple


class BackgroundTasks:
    def __init__(self) -> None:
        self.tasks: List[Tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any]]] = []

    def add_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.tasks.append((func, args, kwargs))
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(result)
            else:
                loop.create_task(result)
