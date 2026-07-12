"""Bitbucket — публичный API workspace (личный workspace = username)."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class BitbucketPlugin(BasePlugin):

    name = "Bitbucket"
    domain = "bitbucket.org"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username
        url = f"https://api.bitbucket.org/2.0/workspaces/{username}"

        try:
            data = await HttpClient.json(url)
        except Exception:
            return []

        if not data or data.get("type") == "error" or not data.get("slug"):
            return []

        links = data.get("links") or {}
        avatar = (links.get("avatar") or {}).get("href")
        html = (links.get("html") or {}).get("href")

        return [
            SearchResult(
                service=self.name,
                username=data.get("slug") or username,
                display_name=data.get("name") or None,
                avatar_url=avatar,
                created_at=data.get("created_on"),
                profile_url=html or f"https://bitbucket.org/{username}/",
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=data,
            )
        ]
