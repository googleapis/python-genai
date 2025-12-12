import typing
from abc import ABC, abstractmethod

from ._types import Headers

class GeminiNextGenAPIClientAdapter(ABC):
    @abstractmethod
    def is_vertex_ai(self) -> bool:
        ...

    @abstractmethod
    def get_project(self) -> str | None:
        ...

    @abstractmethod
    def get_location(self) -> str | None:
        ...

    @abstractmethod
    def get_auth_headers(self) -> dict[str, str] | None:
        ...
