from __future__ import annotations

from core.http import HttpClient
from core.models import (
    SearchRequest,
    SearchResult,
)

from plugins.base import BasePlugin


class GitHubPlugin(BasePlugin):

    name = "GitHub"

    domain = "github.com"

    async def search(
        self,
        request: SearchRequest
    ) -> list[SearchResult]:

        url = f"https://api.github.com/users/{request.username}"

        try:

            data = await HttpClient.json(url)

        except Exception:

            return []

        return [

            SearchResult(

                service=self.name,

                username=data.get("login"),

                display_name=data.get("name"),

                biography=data.get("bio"),

                avatar_url=data.get("avatar_url"),

                website=data.get("blog"),

                followers=data.get("followers"),

                profile_url=data.get("html_url"),

                exists=True,

                similarity=100,

                created_at=data.get("created_at"),

                raw_data=data

            )

        ]