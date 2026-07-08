"""Bluesky — публичный XRPC API профиля."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class BlueskyPlugin(BasePlugin):

    name = "Bluesky"
    domain = "bsky.app"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username

        # Пользователь мог ввести полный хэндл или короткий ник.
        if "." in username:
            handle = username
        else:
            handle = f"{username}.bsky.social"

        url = (
            "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile"
            f"?actor={handle}"
        )

        try:
            data = await HttpClient.json(url)
        except Exception:
            return []

        if not data or not data.get("handle"):
            return []

        return [
            SearchResult(
                service=self.name,
                username=data.get("handle"),
                display_name=data.get("displayName") or None,
                biography=data.get("description") or None,
                avatar_url=data.get("avatar") or None,
                followers=data.get("followersCount"),
                created_at=data.get("createdAt"),
                profile_url=f"https://bsky.app/profile/{data.get('handle')}",
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=data,
            )
        ]
