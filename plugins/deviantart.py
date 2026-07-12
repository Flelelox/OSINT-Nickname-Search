"""DeviantArt — проверка публичного профиля."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class DeviantArtPlugin(ExistencePlugin):

    name = "DeviantArt"
    domain = "deviantart.com"
    url_template = "https://www.deviantart.com/{username}"
    # Может ограничивать автоматические запросы — помечаем как ненадёжный.
    reliable = False
