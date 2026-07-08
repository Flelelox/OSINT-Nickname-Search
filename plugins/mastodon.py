"""Mastodon — публичный API аккаунта (инстанс mastodon.social)."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class MastodonPlugin(BasePlugin):

    name = "Mastodon"
    domain = "mastodon.social"

    # Опрашиваем крупнейший публичный инстанс.
    instance = "mastodon.social"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username
        url = (
            f"https://{self.instance}/api/v1/accounts/lookup"
            f"?acct={username}"
        )

        try:
            data = await HttpClient.json(url)
        except Exception:
            return []

        if not data or not data.get("username"):
            return []

        # У Mastodon описание — в HTML; отдаём как есть (короткое).
        note = data.get("note") or ""

        return [
            SearchResult(
                service=self.name,
                username=data.get("username"),
                display_name=data.get("display_name") or None,
                biography=note or None,
                avatar_url=data.get("avatar_static") or data.get("avatar"),
                followers=data.get("followers_count"),
                created_at=data.get("created_at"),
                profile_url=data.get("url"),
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=data,
            )
        ]
