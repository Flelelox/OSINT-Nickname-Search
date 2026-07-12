"""
Поиск через поисковые системы.

Использует публичные поисковые системы
для поиска открытых профилей.
"""

from __future__ import annotations

from urllib.parse import quote

from core.http import HttpClient


class SearchProvider:

    def __init__(self):

        self.http = HttpClient()

    # =====================================================

    async def duckduckgo(self, query: str) -> str:

        url = (
            "https://html.duckduckgo.com/html/?q="
            + quote(query)
        )

        response = await self.http.get(url)

        return response.text

    # =====================================================

    async def bing(self, query: str) -> str:

        url = (
            "https://www.bing.com/search?q="
            + quote(query)
        )

        response = await self.http.get(url)

        return response.text

    # =====================================================

    async def search_site(

        self,

        site: str,

        username: str

    ) -> str:

        query = f"site:{site} {username}"

        return await self.duckduckgo(query)