"""
Единый движок поиска.

Объединяет весь конвейер:
1. генерация вариантов ника;
2. параллельный опрос всех включённых плагинов по каждому варианту;
3. дедупликация и расчёт похожести относительно исходного ника;
4. фильтрация по порогу совпадения;
5. корреляция аккаунтов (вероятность одного человека);
6. сортировка результатов.

Заменяет старые SearchManager / core.engine.SearchEngine.
"""

from __future__ import annotations

import asyncio
import time
from typing import Callable, Optional

from core.correlation import correlate, enrich_avatar_hashes
from core.logger import get_logger
from core.models import SearchRequest, SearchResult
from core.similarity import Similarity
from core.variants import generate_variants
from plugins.base import BasePlugin
from plugins.loader import load_plugins

log = get_logger("ENGINE")

# Сколько вариантов ника опрашивать максимум (баланс охват/скорость).
MAX_VARIANTS = 8

ProgressCb = Optional[Callable[[int, int], None]]


class SearchEngine:

    def __init__(self, enabled_services: Optional[list[str]] = None):

        self.plugins: list[BasePlugin] = load_plugins()

        # Если передан список — включаем только выбранные сервисы.
        if enabled_services is not None:
            wanted = set(enabled_services)
            for plugin in self.plugins:
                plugin.enabled = plugin.name in wanted

        log.info(f"Loaded {len(self.plugins)} plugins")

    # ------------------------------------------------------
    # Список доступных сервисов (имя, включён ли, надёжен ли)
    # ------------------------------------------------------

    def services(self) -> list[tuple[str, bool, bool]]:
        return [
            (p.name, p.enabled, getattr(p, "reliable", True))
            for p in sorted(self.plugins, key=lambda x: x.name.lower())
        ]

    # ------------------------------------------------------
    # Запуск одного плагина по одному варианту
    # ------------------------------------------------------

    async def _run_plugin(
        self,
        plugin: BasePlugin,
        variant: str,
        threshold: int,
    ) -> list[SearchResult]:

        request = SearchRequest(username=variant, similarity=threshold)

        try:
            results = await plugin.search(request)
        except Exception as e:  # noqa: BLE001
            log.warning(f"{plugin.name} failed on '{variant}': {e}")
            return []

        for r in results:
            r.query = variant

        return results

    # ------------------------------------------------------
    # Дедупликация
    # ------------------------------------------------------

    @staticmethod
    def _dedupe(results: list[SearchResult]) -> list[SearchResult]:
        unique: dict[tuple, SearchResult] = {}
        for r in results:
            key = (r.service, (r.profile_url or "").lower())
            # оставляем вариант с большей похожестью
            if key not in unique or r.similarity > unique[key].similarity:
                unique[key] = r
        return list(unique.values())

    # ------------------------------------------------------
    # Основной поиск
    # ------------------------------------------------------

    async def search(
        self,
        username: str,
        threshold: int = 80,
        search_similar: bool = True,
        correlate_identities: bool = True,
        progress: ProgressCb = None,
    ) -> list[SearchResult]:

        username = username.strip()
        if not username:
            return []

        started = time.time()

        variants = generate_variants(
            username,
            include_similar=search_similar,
            limit=MAX_VARIANTS,
        )

        enabled = [p for p in self.plugins if p.enabled]

        log.info(
            f"Search '{username}': {len(variants)} variants "
            f"x {len(enabled)} services"
        )

        tasks = [
            asyncio.create_task(self._run_plugin(p, variant, threshold))
            for variant in variants
            for p in enabled
        ]

        total = len(tasks)
        done = 0
        collected: list[SearchResult] = []

        for coro in asyncio.as_completed(tasks):
            batch = await coro
            collected.extend(batch)
            done += 1
            if progress:
                progress(done, total)

        # Дедуп + похожесть относительно исходного ника.
        results = self._dedupe(collected)

        for r in results:
            matched = r.username or r.query or ""
            r.similarity = Similarity.score(username, matched)

        # Фильтр по порогу; точное совпадение по нику оставляем всегда.
        low = username.lower()
        filtered = [
            r for r in results
            if r.similarity >= threshold
            or (r.query and r.query.lower() == low)
            or (r.username and r.username.lower() == low)
        ]

        # Корреляция личностей (скачивание аватаров + группировка).
        if correlate_identities and filtered:
            await enrich_avatar_hashes(filtered)
            correlate(filtered, username)
        else:
            for r in filtered:
                r.identity_score = r.similarity

        # Сортировка: сперва уверенность, затем похожесть.
        filtered.sort(
            key=lambda r: (r.identity_score, r.similarity),
            reverse=True,
        )

        log.info(
            f"Done '{username}': {len(filtered)} results "
            f"in {time.time() - started:.1f}s"
        )

        return filtered
