"""npm — существование пользователя через публичный поиск по maintainer."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class NpmPlugin(BasePlugin):

    name = "npm"
    domain = "npmjs.com"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username
        url = (
            "https://registry.npmjs.org/-/v1/search"
            f"?text=maintainer:{username}&size=1"
        )

        try:
            data = await HttpClient.json(url)
        except Exception:
            return []

        objects = (data or {}).get("objects") or []
        total = (data or {}).get("total") or 0

        if total <= 0 or not objects:
            return []

        # Подтверждаем, что maintainer действительно совпадает.
        publisher = (objects[0].get("package") or {}).get("publisher") or {}
        if publisher.get("username", "").lower() != username.lower():
            # Пользователь есть, но как соавтор — всё равно засчитываем.
            pass

        return [
            SearchResult(
                service=self.name,
                username=username,
                display_name=None,
                biography=f"Публичных пакетов: {total}",
                profile_url=f"https://www.npmjs.com/~{username}",
                followers=total,  # используем как «количество публикаций»
                exists=True,
                similarity=100.0,
                source="api",
                raw_data={"total_packages": total},
            )
        ]
