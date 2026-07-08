"""Hugging Face — публичный API профиля (overview)."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class HuggingFacePlugin(BasePlugin):

    name = "Hugging Face"
    domain = "huggingface.co"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username
        url = f"https://huggingface.co/api/users/{username}/overview"

        try:
            data = await HttpClient.json(url)
        except Exception:
            return []

        if not data or not (data.get("user") or data.get("name")):
            return []

        # Разные версии API кладут поля по-разному.
        user = data.get("user") or data.get("name") or username
        avatar = data.get("avatarUrl") or data.get("avatar")
        if avatar and avatar.startswith("/"):
            avatar = "https://huggingface.co" + avatar

        return [
            SearchResult(
                service=self.name,
                username=user,
                display_name=data.get("fullname") or None,
                avatar_url=avatar or None,
                followers=data.get("numFollowers"),
                profile_url=f"https://huggingface.co/{username}",
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=data,
            )
        ]
