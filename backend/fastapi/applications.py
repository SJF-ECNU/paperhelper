from __future__ import annotations

from __future__ import annotations

import asyncio
import inspect
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from .background import BackgroundTasks
from .dependencies import Depends


Handler = Callable[..., Any]
Route = Tuple[str, str, Handler]


def _paths_match(pattern: str, path: str) -> bool:
    if pattern == path:
        return True
    pattern_parts = pattern.strip("/").split("/")
    path_parts = path.strip("/").split("/")
    if len(pattern_parts) != len(path_parts):
        return False
    for p_part, actual in zip(pattern_parts, path_parts):
        if p_part.startswith("{") and p_part.endswith("}"):
            continue
        if p_part != actual:
            return False
    return True


def _extract_params(pattern: str, path: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    pattern_parts = pattern.strip("/").split("/")
    path_parts = path.strip("/").split("/")
    for p_part, actual in zip(pattern_parts, path_parts):
        if p_part.startswith("{") and p_part.endswith("}"):
            params[p_part[1:-1]] = actual
    return params


class FastAPI:
    def __init__(self, title: str | None = None, version: str | None = None) -> None:
        self.title = title
        self.version = version
        self.routes: List[Tuple[str, str, Handler]] = []
        self.dependency_overrides: Dict[Callable[..., Any], Callable[..., Any]] = {}
        self._event_handlers: Dict[str, list[Callable[[], Any]]] = defaultdict(list)

    def add_api_route(self, path: str, endpoint: Handler, methods: list[str]) -> None:
        for method in methods:
            self.routes.append((method.upper(), path, endpoint))

    def post(self, path: str, response_model: Any | None = None) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self.add_api_route(path, func, ["POST"])
            return func

        return decorator

    def get(self, path: str, response_model: Any | None = None) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self.add_api_route(path, func, ["GET"])
            return func

        return decorator

    def on_event(self, event_type: str) -> Callable[[Callable[[], Any]], Callable[[], Any]]:
        def decorator(func: Callable[[], Any]) -> Callable[[], Any]:
            self._event_handlers[event_type].append(func)
            return func

        return decorator

    def add_middleware(self, middleware_class: Any, **kwargs: Any) -> None:  # pragma: no cover - no-op
        return None

    def _get_handler(self, method: str, path: str) -> tuple[Handler, Dict[str, str]]:
        for registered_method, pattern, handler in self.routes:
            if registered_method != method.upper():
                continue
            if _paths_match(pattern, path):
                return handler, _extract_params(pattern, path)
        raise LookupError(f"Route not found for {method} {path}")

    def _resolve_dependency(self, dependency: Depends) -> Any:
        callable_obj = dependency.dependency
        override = self.dependency_overrides.get(callable_obj)
        target = override or callable_obj
        return target()

    async def _execute(self, handler: Handler, kwargs: Dict[str, Any]) -> Any:
        result = handler(**kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    def _build_kwargs(self, handler: Handler, request_data: Dict[str, Any]) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        signature = inspect.signature(handler)
        for name, parameter in signature.parameters.items():
            annotation = parameter.annotation
            if annotation is BackgroundTasks or annotation == "BackgroundTasks":
                kwargs[name] = BackgroundTasks()
                continue
            if isinstance(parameter.default, Depends):
                kwargs[name] = self._resolve_dependency(parameter.default)
                continue
            if name in request_data:
                kwargs[name] = request_data[name]
            elif parameter.default is not inspect._empty:
                kwargs[name] = parameter.default
        return kwargs

    def trigger_event(self, event_type: str) -> None:
        for handler in self._event_handlers.get(event_type, []):
            handler()

    def _call_route(self, method: str, path: str, request_data: Dict[str, Any]) -> Any:
        handler, path_params = self._get_handler(method, path)
        all_data = dict(request_data)
        all_data.update(path_params)
        kwargs = self._build_kwargs(handler, all_data)
        return asyncio.run(self._execute(handler, kwargs))
