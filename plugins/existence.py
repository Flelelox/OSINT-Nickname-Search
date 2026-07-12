"""
Базовый плагин проверки существования профиля по URL.

Многие сервисы не отдают публичного API, но по адресу
профиля можно понять, существует ли аккаунт: по HTTP-статусу
и/или по характерным маркерам в теле страницы.

ВАЖНО: используются только публично доступные страницы,
никакой обход защиты/аутентификации не выполняется. Для
сервисов, которые активно блокируют ботов, результат
помечается как ненадёжный (reliable = False).
"""

from __future__ import annotations

from core.http import HttpClient
from core.models import SearchRequest, SearchResult
from plugins.base import BasePlugin


class ExistencePlugin(BasePlugin):

    # Шаблон адреса профиля, например "https://t.me/{username}".
    url_template: str = ""

    # Статусы, однозначно означающие "профиля нет".
    not_found_status: tuple[int, ...] = (404, 410)

    # Подстроки в теле страницы, означающие "профиля нет"
    # (для сервисов с soft-404, отвечающих 200 на любой URL).
    not_found_markers: tuple[str, ...] = ()

    # Если задано — профиль считается найденным только когда
    # в теле присутствует хотя бы один из этих маркеров.
    found_markers: tuple[str, ...] = ()

    # Нужно ли скачивать тело страницы (иначе хватит статуса).
    check_body: bool = False

    # Насколько источнику можно доверять. Для Instagram/X/FB и т.п.
    # ставим False — они часто блокируют ботов, возможны ложные ответы.
    reliable: bool = True

    # Таймаут одной проверки (сек). Короче общего, чтобы не подвисать.
    timeout: int = 6

    async def search(self, request: SearchRequest) -> list[SearchResult]:

        username = request.username

        if not self.url_template:
            return []

        url = self.url_template.format(username=username)

        need_body = (
            self.check_body
            or self.not_found_markers
            or self.found_markers
        )

        try:
            if need_body:
                status, text = await HttpClient.fetch(
                    url, timeout=self.timeout, retries=1
                )
            else:
                status = await HttpClient.status(
                    url, timeout=self.timeout, retries=1
                )
                text = ""
        except Exception:
            # Сеть/таймаут/блокировка — считаем, что не нашли.
            return []

        if not self._exists(status, text):
            return []

        note = "" if self.reliable else " (проверка ненадёжна)"

        return [
            SearchResult(
                service=self.name + note,
                username=username,
                profile_url=url,
                exists=True,
                similarity=100.0,
                source="existence",
            )
        ]

    def _exists(self, status: int, text: str) -> bool:
        """Решение о существовании профиля по статусу и телу."""

        if status in self.not_found_status:
            return False

        if status >= 400:
            return False

        low = text.lower()

        for marker in self.not_found_markers:
            if marker.lower() in low:
                return False

        if self.found_markers:
            return any(m.lower() in low for m in self.found_markers)

        return 200 <= status < 400
