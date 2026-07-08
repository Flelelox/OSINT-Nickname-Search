"""Keybase — публичный API user/lookup."""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class KeybasePlugin(BasePlugin):

    name = "Keybase"
    domain = "keybase.io"

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username
        url = (
            "https://keybase.io/_/api/1.0/user/lookup.json"
            f"?usernames={username}"
        )

        try:
            payload = await HttpClient.json(url)
        except Exception:
            return []

        them = (payload or {}).get("them") or []
        if not them or not them[0]:
            return []

        user = them[0]
        basics = user.get("basics") or {}
        profile = user.get("profile") or {}
        pictures = user.get("pictures") or {}
        primary = (pictures.get("primary") or {}) if pictures else {}

        return [
            SearchResult(
                service=self.name,
                username=basics.get("username") or username,
                display_name=profile.get("full_name") or None,
                biography=profile.get("bio") or None,
                avatar_url=primary.get("url") or None,
                website=profile.get("website") or None,
                profile_url=f"https://keybase.io/{username}",
                exists=True,
                similarity=100.0,
                source="api",
                raw_data=user,
            )
        ]
