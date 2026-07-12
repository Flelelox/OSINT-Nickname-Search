from __future__ import annotations

import asyncio

from core.models import SearchRequest, SearchResult
from plugins.loader import load_plugins


class PluginManager:

    def __init__(self):

        self.plugins = load_plugins()

    async def search(
        self,
        username: str,
        similarity: int = 80
    ) -> list[SearchResult]:

        request = SearchRequest(
            username=username,
            similarity=similarity
        )

        tasks = [

            plugin.search(request)

            for plugin in self.plugins

            if plugin.enabled

        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        output: list[SearchResult] = []

        for result in results:

            if isinstance(result, Exception):
                continue

            output.extend(result)

        return output