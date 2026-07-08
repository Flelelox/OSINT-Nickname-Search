"""
Кэш результатов поиска.

Используется для хранения результатов запросов
с ограниченным временем жизни (TTL).
"""

from __future__ import annotations

import time
from threading import Lock
from typing import Any


class Cache:

    def __init__(self, ttl: int = 600):

        # Время жизни записи (секунды)
        self.ttl = ttl

        # Хранилище
        self._cache: dict[str, tuple[float, Any]] = {}

        # Потокобезопасность
        self._lock = Lock()

    # =====================================================
    # Получить значение
    # =====================================================

    def get(self, key: str):

        with self._lock:

            item = self._cache.get(key)

            if item is None:
                return None

            expires, value = item

            if expires < time.time():

                del self._cache[key]

                return None

            return value

    # =====================================================
    # Сохранить значение
    # =====================================================

    def set(self, key: str, value: Any):

        with self._lock:

            self._cache[key] = (
                time.time() + self.ttl,
                value
            )

    # =====================================================
    # Проверить наличие
    # =====================================================

    def has(self, key: str):

        return self.get(key) is not None

    # =====================================================
    # Очистить весь кэш
    # =====================================================

    def clear(self):

        with self._lock:

            self._cache.clear()

    # =====================================================
    # Удалить одну запись
    # =====================================================

    def remove(self, key: str):

        with self._lock:

            self._cache.pop(key, None)

    # =====================================================
    # Очистить устаревшие записи
    # =====================================================

    def cleanup(self):

        now = time.time()

        with self._lock:

            expired = [

                key

                for key, (expires, _)

                in self._cache.items()

                if expires < now

            ]

            for key in expired:

                del self._cache[key]