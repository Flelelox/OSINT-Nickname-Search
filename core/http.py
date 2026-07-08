"""
Асинхронный HTTP-клиент проекта.

Возможности:
- единый пул соединений (httpx.AsyncClient);
- ограничение количества одновременных запросов (semaphore);
- повторные попытки при временных ошибках;
- кэширование ответов с TTL (core.cache.Cache).
"""

from __future__ import annotations

import asyncio

import httpx

from core.cache import Cache
from core.logger import get_logger

log = get_logger("HTTP")

# Максимум одновременных запросов ко всем сервисам сразу.
MAX_CONCURRENCY = 20

# Сколько раз повторять запрос при временной ошибке.
RETRIES = 2

# Таймаут одного запроса (секунды).
TIMEOUT = 10

# Время жизни кэша ответов (секунды).
CACHE_TTL = 600

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/138.0 Safari/537.36"
)


class HttpClient:

    _client: httpx.AsyncClient | None = None

    _semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    _cache = Cache(ttl=CACHE_TTL)

    # =====================================================

    @classmethod
    async def client(cls) -> httpx.AsyncClient:

        if cls._client is None:

            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(TIMEOUT),
                follow_redirects=True,
                headers={"User-Agent": USER_AGENT},
            )

        return cls._client

    # =====================================================
    # Низкоуровневый GET с ретраями
    # =====================================================

    @classmethod
    async def get(cls, url: str, **kwargs) -> httpx.Response:

        # Число попыток можно переопределить на запрос (retries=1).
        retries = kwargs.pop("retries", RETRIES)

        async with cls._semaphore:

            client = await cls.client()

            last_error: Exception | None = None

            for attempt in range(retries):

                try:
                    return await client.get(url, **kwargs)

                except Exception as e:  # noqa: BLE001 - логируем и повторяем

                    last_error = e
                    log.warning(f"GET retry {attempt + 1}: {url}")

                    if attempt < retries - 1:
                        await asyncio.sleep(1)

            raise last_error  # type: ignore[misc]

    # =====================================================

    @classmethod
    async def post(cls, url: str, **kwargs) -> httpx.Response:

        async with cls._semaphore:
            client = await cls.client()
            return await client.post(url, **kwargs)

    # =====================================================
    # Кэшируемые обёртки
    # =====================================================

    @classmethod
    async def text(cls, url: str, **kwargs) -> str:

        key = f"text:{url}"
        cached = cls._cache.get(key)
        if cached is not None:
            return cached

        response = await cls.get(url, **kwargs)
        cls._cache.set(key, response.text)
        return response.text

    @classmethod
    async def json(cls, url: str, **kwargs):

        key = f"json:{url}"
        cached = cls._cache.get(key)
        if cached is not None:
            return cached

        response = await cls.get(url, **kwargs)
        data = response.json()
        cls._cache.set(key, data)
        return data

    @classmethod
    async def fetch(cls, url: str, **kwargs) -> tuple[int, str]:
        """
        Вернуть (status_code, text). Используется проверкой
        существования профиля. Результат кэшируется.
        """
        key = f"fetch:{url}"
        cached = cls._cache.get(key)
        if cached is not None:
            return cached

        response = await cls.get(url, **kwargs)
        result = (response.status_code, response.text)
        cls._cache.set(key, result)
        return result

    @classmethod
    async def status(cls, url: str, **kwargs) -> int:
        """Вернуть только HTTP-статус (с кэшем)."""
        status, _ = await cls.fetch(url, **kwargs)
        return status

    @classmethod
    async def bytes(cls, url: str, **kwargs) -> bytes:
        """Скачать сырые байты (например, аватар). Без кэша."""
        response = await cls.get(url, **kwargs)
        return response.content

    # =====================================================

    @classmethod
    async def close(cls):

        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None
