"""GitLab — публичный API поиска пользователя по username."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class GitLabPlugin(BasePlugin):

    name = "GitLab"
    domain = "gitlab.com"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        url = f"https://gitlab.com/api/v4/users?username={request.username}"

        try:
            data = await HttpClient.json(url)
        except Exception:
            return []

        if not isinstance(data, list) or not data:
            return []

        user = data[0]

        return [
            SearchResult(
                service=self.name,
                username=user.get("username"),
                display_name=user.get("name"),
                avatar_url=user.get("avatar_url"),
                profile_url=user.get("web_url"),
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=user,
            )
        ]
