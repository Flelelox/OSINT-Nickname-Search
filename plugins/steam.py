"""Steam Community — проверка публичного профиля по vanity-URL."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class SteamPlugin(ExistencePlugin):

    name = "Steam"
    domain = "steamcommunity.com"
    url_template = "https://steamcommunity.com/id/{username}"
    check_body = True
    # Страница отвечает 200 всегда; отсутствие профиля видно по маркеру.
    not_found_markers = ("The specified profile could not be found",)
    reliable = True
