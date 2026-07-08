from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import SearchRequest
from core.models import SearchResult


class BasePlugin(ABC):
    """
    Базовый класс любого источника поиска.
    """

    name: str = "Unknown"

    domain: str = ""

    enabled: bool = True

    @abstractmethod
    async def search(
        self,
        request: SearchRequest
    ) -> list[SearchResult]:
        """
        Выполнить поиск.
        """
        raise NotImplementedError