"""
Модели данных проекта.

Все остальные модули используют эти dataclass вместо словарей.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ============================================================
# Параметры поиска
# ============================================================

@dataclass(slots=True)
class SearchRequest:
    """
    Запрос пользователя.
    """

    username: str
    similarity: int = 80
    search_similar: bool = True


# ============================================================
# Найденный профиль
# ============================================================

@dataclass(slots=True)
class SearchResult:
    """
    Результат поиска по одному сервису.
    """

    service: str

    username: str

    profile_url: str

    exists: bool = False

    similarity: float = 100.0

    display_name: Optional[str] = None

    biography: Optional[str] = None

    avatar_url: Optional[str] = None

    website: Optional[str] = None

    followers: Optional[int] = None

    created_at: Optional[str] = None

    # --- служебные поля ---

    # как получен результат: "api" | "existence" | "search-engine"
    source: str = "api"

    # какой вариант ника дал совпадение (может отличаться от запроса)
    query: Optional[str] = None

    # перцептивный хэш аватара (для сравнения картинок)
    avatar_hash: Optional[str] = None

    # вероятность принадлежности одному человеку (0..100)
    identity_score: float = 0.0

    # номер группы корреляции (-1 = не сгруппирован)
    identity_group: int = -1

    raw_data: dict = field(default_factory=dict)


# ============================================================
# Информация о сервисе
# ============================================================

@dataclass(slots=True)
class ServiceInfo:

    name: str

    domain: str

    enabled: bool = True


# ============================================================
# Итог поиска
# ============================================================

@dataclass(slots=True)
class SearchSession:

    request: SearchRequest

    started: datetime = field(default_factory=datetime.utcnow)

    finished: Optional[datetime] = None

    results: list[SearchResult] = field(default_factory=list)