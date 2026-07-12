"""Reddit — публичный JSON профиля пользователя (about.json)."""

from __future__ import annotations

from datetime import datetime, timezone

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class RedditPlugin(BasePlugin):

    name = "Reddit"
    domain = "reddit.com"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username
        url = f"https://www.reddit.com/user/{username}/about.json"

        try:
            payload = await HttpClient.json(url)
        except Exception:
            return []

        data = (payload or {}).get("data")
        if not data:
            return []

        created = data.get("created_utc")
        created_at = None
        if created:
            created_at = datetime.fromtimestamp(
                created, tz=timezone.utc
            ).isoformat()

        subreddit = data.get("subreddit") or {}

        return [
            SearchResult(
                service=self.name,
                username=data.get("name") or username,
                display_name=subreddit.get("title") or None,
                biography=subreddit.get("public_description") or None,
                avatar_url=(data.get("icon_img") or "").split("?")[0] or None,
                followers=subreddit.get("subscribers"),
                profile_url=f"https://www.reddit.com/user/{username}",
                created_at=created_at,
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=data,
            )
        ]
