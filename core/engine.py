"""
Основной движок поиска OSINT.

Отвечает за:
- загрузку плагинов;
- запуск поиска;
- выполнение поиска сразу по нескольким никнеймам;
- отмену поиска;
- логирование.
"""

from __future__ import annotations

import asyncio
from typing import Iterable

from core.logger import get_logger
from core.models import (
    SearchRequest,
    SearchResult,
)

from plugins.base import BasePlugin
from plugins.loader import load_plugins

log = get_logger("ENGINE")


class SearchEngine:
    """
    Центральный движок поиска.
    """

    def __init__(self) -> None:

        self.plugins: list[BasePlugin] = load_plugins()

        self._cancelled = False

        log.info(f"Loaded {len(self.plugins)} plugins")

        for plugin in self.plugins:
            log.info(f" • {plugin.name}")

    # ==========================================================
    # Отмена поиска
    # ==========================================================

    def cancel(self) -> None:

        self._cancelled = True

    # ==========================================================
    # Сброс отмены
    # ==========================================================

    def reset(self) -> None:

        self._cancelled = False

    # ==========================================================
    # Поиск одного никнейма
    # ==========================================================

    async def search_one(
        self,
        request: SearchRequest
    ) -> list[SearchResult]:

        self.reset()

        tasks = []

        for plugin in self.plugins:

            if not plugin.enabled:
                continue

            tasks.append(
                asyncio.create_task(
                    plugin.search(request)
                )
            )

        results: list[SearchResult] = []

        for task in asyncio.as_completed(tasks):

            if self._cancelled:

                log.warning("Search cancelled")

                for t in tasks:
                    t.cancel()

                break

            try:

                data = await task

                if data:
                    results.extend(data)

            except asyncio.CancelledError:

                pass

            except Exception as e:

                log.exception(e)

        return results

    # ==========================================================
    # Поиск нескольких никнеймов
    # ==========================================================

    async def search_many(
        self,
        usernames: Iterable[str],
        similarity: int = 80,
    ) -> dict[str, list[SearchResult]]:

        output: dict[str, list[SearchResult]] = {}

        for username in usernames:

            if self._cancelled:
                break

            username = username.strip()

            if not username:
                continue

            request = SearchRequest(
                username=username,
                similarity=similarity,
            )

            output[username] = await self.search_one(
                request
            )

        return output

    # ==========================================================
    # Регистрация плагина вручную
    # ==========================================================

    def register(
        self,
        plugin: BasePlugin
    ) -> None:

        self.plugins.append(plugin)

        log.info(
            f"Plugin registered: {plugin.name}"
        )

    # ==========================================================
    # Получить список плагинов
    # ==========================================================

    def plugin_names(self) -> list[str]:

        return [
            plugin.name
            for plugin in self.plugins
            if plugin.enabled
        ]