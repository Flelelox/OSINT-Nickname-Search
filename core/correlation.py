"""
Корреляция аккаунтов: оценка вероятности того, что найденные
профили принадлежат одному человеку.

Учитываются:
- похожесть никнейма;
- совпадение отображаемого имени;
- совпадение биографии;
- общие ссылки и домены сайтов;
- похожесть аватаров (перцептивный хэш).

Профили группируются (union-find) по сильным признакам, каждому
результату выставляется identity_score (0..100) — уверенность,
что это тот же человек, что и в исходном запросе.
"""

from __future__ import annotations

import asyncio
import re

from core.http import HttpClient
from core.imagehash import dhash, similar
from core.models import SearchResult
from core.similarity import Similarity

_URL_RE = re.compile(r"https?://[^\s\"'<>)]+", re.IGNORECASE)
_DOMAIN_RE = re.compile(r"https?://(?:www\.)?([^/\s]+)", re.IGNORECASE)


# ============================================================
# Аватары
# ============================================================

async def enrich_avatar_hashes(results: list[SearchResult]) -> None:
    """
    Скачать аватары и проставить avatar_hash (in-place).
    Работает best-effort: ошибки/таймауты игнорируются.
    """

    async def one(result: SearchResult) -> None:
        if not result.avatar_url:
            return
        try:
            data = await HttpClient.bytes(result.avatar_url, timeout=8)
            result.avatar_hash = dhash(data)
        except Exception:
            result.avatar_hash = None

    targets = [r for r in results if r.avatar_url]
    if targets:
        await asyncio.gather(*(one(r) for r in targets), return_exceptions=True)


# ============================================================
# Вспомогательные извлечения
# ============================================================

def _links(result: SearchResult) -> set[str]:
    text = " ".join(
        filter(None, [result.website, result.biography])
    )
    links = set(_URL_RE.findall(text))
    if result.website:
        links.add(result.website)
    return links


def _domains(result: SearchResult) -> set[str]:
    domains = set()
    for link in _links(result):
        m = _DOMAIN_RE.match(link)
        if m:
            domains.add(m.group(1).lower())
    return domains


def _name(result: SearchResult) -> str:
    return (result.display_name or "").strip().lower()


# ============================================================
# Основная корреляция
# ============================================================

def correlate(
    results: list[SearchResult],
    query: str,
) -> list[SearchResult]:
    """
    Проставить identity_group и identity_score для каждого результата.
    """
    n = len(results)
    if n == 0:
        return results

    # Предвычисляем признаки.
    names = [_name(r) for r in results]
    domains = [_domains(r) for r in results]
    links = [_links(r) for r in results]

    # ---- Union-Find для группировки ----
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        parent[find(a)] = find(b)

    def strong_link(i: int, j: int) -> bool:
        # Совпадение отображаемого имени.
        if names[i] and names[i] == names[j]:
            return True
        # Общий домен сайта.
        if domains[i] & domains[j]:
            return True
        # Общая ссылка.
        if links[i] & links[j]:
            return True
        # Похожие аватары.
        if similar(results[i].avatar_hash, results[j].avatar_hash):
            return True
        # Очень похожие ники.
        if Similarity.score(results[i].username or "", results[j].username or "") >= 88:
            return True
        return False

    for i in range(n):
        for j in range(i + 1, n):
            if strong_link(i, j):
                union(i, j)

    # Нумеруем группы.
    group_ids: dict[int, int] = {}
    for i in range(n):
        root = find(i)
        if root not in group_ids:
            group_ids[root] = len(group_ids)
        results[i].identity_group = group_ids[root]

    # ---- Оценка уверенности ----
    for i, r in enumerate(results):
        # База — похожесть ника на исходный запрос.
        score = Similarity.score(query, r.username or "")

        # Бонусы за подтверждения от других профилей той же группы.
        bonus = 0
        for j, other in enumerate(results):
            if j == i or other.identity_group != r.identity_group:
                continue
            if names[i] and names[i] == names[j]:
                bonus += 15
            if similar(r.avatar_hash, other.avatar_hash):
                bonus += 20
            if domains[i] & domains[j]:
                bonus += 10
            if links[i] & links[j]:
                bonus += 10

        r.identity_score = round(min(100.0, score + min(bonus, 40)), 2)

    return results
