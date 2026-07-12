from __future__ import annotations

from core.http import HttpClient
from core.models import (
    SearchRequest,
    SearchResult,
)

from plugins.base import BasePlugin


class ExistencePlugin(BasePlugin):
    """
    Базовый класс для сервисов без публичного API.

    Принадлежность профиля определяется так же, как в Sherlock:
    по HTTP-статусу и/или по наличию/отсутствию маркера
    "профиль не найден" в теле ответа.

    Наследники задают только атрибуты:

        url_template   - шаблон профиля, {username} подставляется
        error_type     - "status_code" | "message" | "status_and_message"
        error_msg      - строка-маркер отсутствия профиля (для message-режимов)
        request_headers- дополнительные заголовки запроса (опционально)
    """

    url_template: str = ""

    error_type: str = "status_code"

    error_msg: str | None = None

    request_headers: dict | None = None

    async def search(
        self,
        request: SearchRequest
    ) -> list[SearchResult]:

        if not self.url_template:
            return []

        url = self.url_template.format(username=request.username)

        try:

            status, text = await HttpClient.fetch(
                url,
                headers=self.request_headers,
            )

        except Exception:

            return []

        if not self._exists(status, text):
            return []

        return [

            SearchResult(

                service=self.name,

                username=request.username,

                profile_url=url,

                exists=True,

                similarity=100,

                source="existence",

            )

        ]

    def _exists(self, status: int, text: str) -> bool:

        if self.error_type == "status_code":
            return status == 200

        if self.error_type == "message":
            if status != 200:
                return False
            if not self.error_msg:
                return True
            return self.error_msg not in text

        if self.error_type == "status_and_message":
            if status not in (200, 403):
                return False
            if not self.error_msg:
                return status == 200
            return self.error_msg not in text

        return False
