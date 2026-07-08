"""Docker Hub — публичный API пользователя."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class DockerHubPlugin(BasePlugin):

    name = "Docker Hub"
    domain = "hub.docker.com"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username
        url = f"https://hub.docker.com/v2/users/{username}/"

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
                display_name=data.get("full_name") or None,
                avatar_url=data.get("gravatar_url") or None,
                created_at=data.get("date_joined"),
                profile_url=f"https://hub.docker.com/u/{username}",
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=data,
            )
        ]
