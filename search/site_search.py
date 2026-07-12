from __future__ import annotations

import asyncio
import json
from pathlib import Path

from search.search_provider import SearchProvider
from search.parser import SearchParser
from search.result_builder import ResultBuilder

from core.models import SearchResult


SERVICES = Path("services/services.json")


class SiteSearcher:

    def __init__(self):

        self.provider = SearchProvider()

        with open(
            SERVICES,
            "r",
            encoding="utf-8"
        ) as f:

            self.sites = json.load(f)

    async def search_site(
        self,
        site: str,
        username: str
    ) -> list[SearchResult]:

        try:

            html = await self.provider.search_site(
                site,
                username
            )

            links = SearchParser.extract_links(html)

            results: list[SearchResult] = []

            for link in links:

                results.append(

                    ResultBuilder.build(

                        service=site,

                        username=username,

                        url=link,

                        similarity=100

                    )

                )

            return results

        except Exception:

            return []

    async def search(
        self,
        username: str
    ) -> list[SearchResult]:

        tasks = [

            asyncio.create_task(

                self.search_site(

                    site,

                    username

                )

            )

            for site in self.sites

        ]

        completed = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        results: list[SearchResult] = []

        for item in completed:

            if isinstance(item, Exception):
                continue

            results.extend(item)

        return results