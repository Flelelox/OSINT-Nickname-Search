"""PyPI — проверка существования публичной страницы пользователя."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class PyPIPlugin(ExistencePlugin):

    name = "PyPI"
    domain = "pypi.org"
    url_template = "https://pypi.org/user/{username}/"
    check_body = True
    # Несуществующий пользователь -> 404. Плюс отсеиваем антибот-страницу,
    # которую PyPI иногда отдаёт с кодом 200 (ложное срабатывание).
    not_found_markers = ("Client Challenge", "Page not found")
    # На части сетей PyPI включает антибот-защиту -> помечаем как ненадёжный.
    reliable = False
