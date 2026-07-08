"""Pinterest — проверка публичного профиля."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class PinterestPlugin(ExistencePlugin):

    name = "Pinterest"
    domain = "pinterest.com"
    url_template = "https://www.pinterest.com/{username}/"
    reliable = False
