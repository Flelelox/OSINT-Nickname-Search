"""VK — проверка публичной страницы (только открытые данные)."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class VkPlugin(ExistencePlugin):

    name = "VK"
    domain = "vk.com"
    url_template = "https://vk.com/{username}"
    check_body = True
    not_found_markers = (
        "This page has been removed",
        "Страница удалена",
        "404 Not Found",
    )
    reliable = False
