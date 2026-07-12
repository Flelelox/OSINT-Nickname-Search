from __future__ import annotations

import asyncio

from core.models import SearchResult

from search.plugin_manager import PluginManager
from search.site_search import SiteSearcher

# Максимум секунд, который ждём медленный site-search (скрейпинг DuckDuckGo).
# Плагины (GitHub и т.п.) при этом всё равно попадут в результат.
SITE_SEARCH_TIMEOUT = 20


class SearchManager:

    def __init__(self):

        self.plugins = PluginManager()

        self.searcher = SiteSearcher()

    async def search(

        self,

        username: str,

        similarity: int = 80

    ) -> list[SearchResult]:

        plugin_results = await self.plugins.search(

            username,

            similarity

        )

        try:

            site_results = await asyncio.wait_for(

                self.searcher.search(username),

                timeout=SITE_SEARCH_TIMEOUT,

            )

        except (asyncio.TimeoutError, Exception):

            site_results = []

        results = plugin_results + site_results

        return self.remove_duplicates(

            results

        )

    @staticmethod
    def remove_duplicates(

        results: list[SearchResult]

    ) -> list[SearchResult]:

        unique = {}

        for result in results:

            key = (

                result.service,

                result.profile_url

            )

            unique[key] = result

        return sorted(

            unique.values(),

            key=lambda x: x.similarity,

            reverse=True

        )