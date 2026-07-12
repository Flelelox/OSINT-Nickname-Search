"""dev.to — публичный API пользователя."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class DevToPlugin(BasePlugin):

    name = "dev.to"
    domain = "dev.to"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username
        url = f"https://dev.to/api/users/by_username?url={username}"

        try:
            data = await HttpClient.json(url)
        except Exception:
            return []

        if not data or not data.get("username"):
            return []

        return [
            SearchResult(
                service=self.name,
                username=data.get("username"),
                display_name=data.get("name") or None,
                biography=data.get("summary") or None,
                avatar_url=data.get("profile_image") or None,
                website=data.get("website_url") or None,
                created_at=data.get("joined_at"),
                profile_url=f"https://dev.to/{username}",
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=data,
            )
        ]
