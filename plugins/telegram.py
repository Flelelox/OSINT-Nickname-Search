"""Telegram — проверка публичного username через t.me (только открытые данные)."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class TelegramPlugin(ExistencePlugin):

    name = "Telegram"
    domain = "t.me"
    url_template = "https://t.me/{username}"
    check_body = True
    # Публичная страница профиля/канала содержит этот маркер.
    found_markers = ("tgme_page_title",)
    reliable = True
