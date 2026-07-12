from __future__ import annotations

from plugins._existence_base import ExistencePlugin


# ============================================================
# Status-code based (надёжные: 200 = есть, 404 = нет)
# ============================================================

class GitLabPlugin(ExistencePlugin):
    name = "GitLab"
    domain = "gitlab.com"
    url_template = "https://gitlab.com/{username}"
    error_type = "status_code"


class NpmPlugin(ExistencePlugin):
    name = "npm"
    domain = "npmjs.com"
    url_template = "https://www.npmjs.com/~{username}"
    error_type = "status_code"


class PyPIPlugin(ExistencePlugin):
    name = "PyPI"
    domain = "pypi.org"
    url_template = "https://pypi.org/user/{username}/"
    error_type = "status_code"


class KeybasePlugin(ExistencePlugin):
    name = "Keybase"
    domain = "keybase.io"
    url_template = "https://keybase.io/{username}"
    error_type = "status_code"


class HabrPlugin(ExistencePlugin):
    name = "Habr"
    domain = "habr.com"
    url_template = "https://habr.com/ru/users/{username}/"
    error_type = "status_code"


class LeetCodePlugin(ExistencePlugin):
    name = "LeetCode"
    domain = "leetcode.com"
    url_template = "https://leetcode.com/{username}/"
    error_type = "status_code"


class ChessComPlugin(ExistencePlugin):
    name = "Chess.com"
    domain = "chess.com"
    url_template = "https://www.chess.com/member/{username}"
    error_type = "status_code"


class SoundCloudPlugin(ExistencePlugin):
    name = "SoundCloud"
    domain = "soundcloud.com"
    url_template = "https://soundcloud.com/{username}"
    error_type = "status_code"


class BehancePlugin(ExistencePlugin):
    name = "Behance"
    domain = "behance.net"
    url_template = "https://www.behance.net/{username}"
    error_type = "status_code"


class KagglePlugin(ExistencePlugin):
    name = "Kaggle"
    domain = "kaggle.com"
    url_template = "https://www.kaggle.com/{username}"
    error_type = "status_code"


class PinterestPlugin(ExistencePlugin):
    name = "Pinterest"
    domain = "pinterest.com"
    url_template = "https://www.pinterest.com/{username}/"
    error_type = "status_code"


class MediumPlugin(ExistencePlugin):
    name = "Medium"
    domain = "medium.com"
    url_template = "https://medium.com/@{username}"
    error_type = "status_code"


class DeviantArtPlugin(ExistencePlugin):
    name = "DeviantArt"
    domain = "deviantart.com"
    url_template = "https://www.deviantart.com/{username}"
    error_type = "status_code"


class TrelloPlugin(ExistencePlugin):
    name = "Trello"
    domain = "trello.com"
    url_template = "https://trello.com/{username}"
    error_type = "status_code"


class VimeoPlugin(ExistencePlugin):
    name = "Vimeo"
    domain = "vimeo.com"
    url_template = "https://vimeo.com/{username}"
    error_type = "status_code"


class FlickrPlugin(ExistencePlugin):
    name = "Flickr"
    domain = "flickr.com"
    url_template = "https://www.flickr.com/people/{username}"
    error_type = "status_code"


class KickstarterPlugin(ExistencePlugin):
    name = "Kickstarter"
    domain = "kickstarter.com"
    url_template = "https://www.kickstarter.com/profile/{username}"
    error_type = "status_code"


class ProductHuntPlugin(ExistencePlugin):
    name = "Product Hunt"
    domain = "producthunt.com"
    url_template = "https://www.producthunt.com/@{username}"
    error_type = "status_code"


class CodePenPlugin(ExistencePlugin):
    name = "CodePen"
    domain = "codepen.io"
    url_template = "https://codepen.io/{username}"
    error_type = "status_code"


class ReplitPlugin(ExistencePlugin):
    name = "Replit"
    domain = "replit.com"
    url_template = "https://replit.com/@{username}"
    error_type = "status_code"


# ============================================================
# Message-based (сайт всегда отдаёт 200, ищем маркер "не найден")
# ============================================================

class SteamPlugin(ExistencePlugin):
    name = "Steam"
    domain = "steamcommunity.com"
    url_template = "https://steamcommunity.com/id/{username}"
    error_type = "message"
    error_msg = "The specified profile could not be found"


class HackerNewsPlugin(ExistencePlugin):
    name = "Hacker News"
    domain = "news.ycombinator.com"
    url_template = "https://news.ycombinator.com/user?id={username}"
    error_type = "message"
    error_msg = "No such user"


class CodeforcesPlugin(ExistencePlugin):
    name = "Codeforces"
    domain = "codeforces.com"
    url_template = "https://codeforces.com/profile/{username}"
    error_type = "message"
    error_msg = "Redirecting"  # codeforces возвращает редирект-страницу для несуществующих


class TikTokPlugin(ExistencePlugin):
    name = "TikTok"
    domain = "tiktok.com"
    url_template = "https://www.tiktok.com/@{username}"
    error_type = "message"
    error_msg = "Couldn't find this account"


# ============================================================
# ВНИМАНИЕ: сайты ниже активно блокируют автоматические запросы
# (антибот-защита, требуют cookies/JS-рендер). Простой GET-запрос
# часто будет давать ложные "не найдено" или капчу вместо ответа.
# Оставлены как заготовки — протестируйте перед включением в общий
# список и при необходимости добавьте заголовки/прокси.
# ============================================================

class InstagramPlugin(ExistencePlugin):
    name = "Instagram"
    domain = "instagram.com"
    url_template = "https://www.instagram.com/{username}/"
    error_type = "status_and_message"
    error_msg = "Sorry, this page isn't available"
    enabled = False  # включите, если протестируете и убедитесь в стабильности


class VKPlugin(ExistencePlugin):
    name = "VK"
    domain = "vk.com"
    url_template = "https://vk.com/{username}"
    error_type = "message"
    error_msg = "Page not found"
    enabled = False  # часто требует cookies/JS, проверьте перед включением
