from __future__ import annotations

import asyncio

from plugins.base import BasePlugin

from core.models import (
    SearchRequest,
    SearchResult
)


class ExamplePlugin(BasePlugin):

    name = "Example"

    domain = "example.com"

    async def search(

        self,

        request: SearchRequest

    ) -> list[SearchResult]:

        await asyncio.sleep(1)

        return [

            SearchResult(

                service=self.name,

                username=request.username,

                profile_url=f"https://example.com/{request.username}",

                exists=True,

                similarity=100

            )

        ]