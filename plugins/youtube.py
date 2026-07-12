"""YouTube — проверка публичного канала по @handle."""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class YouTubePlugin(ExistencePlugin):

    name = "YouTube"
    domain = "youtube.com"
    url_template = "https://www.youtube.com/@{username}"
    # Несуществующий handle отдаёт честный 404.
    reliable = True
