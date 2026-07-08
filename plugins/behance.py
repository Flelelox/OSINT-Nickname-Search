"""Behance — проверка публичного профиля."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class BehancePlugin(ExistencePlugin):

    name = "Behance"
    domain = "behance.net"
    url_template = "https://www.behance.net/{username}"
    # Несуществующий профиль отдаёт 404.
    reliable = True
