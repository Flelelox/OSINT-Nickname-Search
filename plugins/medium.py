"""Medium — проверка публичного профиля по @username."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class MediumPlugin(ExistencePlugin):

    name = "Medium"
    domain = "medium.com"
    url_template = "https://medium.com/@{username}"
    reliable = False
