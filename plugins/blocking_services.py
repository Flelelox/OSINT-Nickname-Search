"""
Сервисы, которые активно ограничивают автоматические запросы
(login-wall, антибот-защита): Instagram, X, Facebook, LinkedIn,
TikTok, Threads, Twitch.

Проверка сводится к обращению к публичной странице профиля —
БЕЗ входа в аккаунт и без обхода защиты. Из-за этого результат
ненадёжен, поэтому все они по умолчанию ВЫКЛЮЧЕНЫ (enabled = False)
и помечены reliable = False. Пользователь может включить их
вручную в настройках, понимая ограничения.
"""

from __future__ import annotations

from plugins.existence import ExistencePlugin


class _Blocking(ExistencePlugin):
    enabled = False
    reliable = False


class InstagramPlugin(_Blocking):
    name = "Instagram"
    domain = "instagram.com"
    url_template = "https://www.instagram.com/{username}/"


class XPlugin(_Blocking):
    name = "X (Twitter)"
    domain = "x.com"
    url_template = "https://x.com/{username}"


class FacebookPlugin(_Blocking):
    name = "Facebook"
    domain = "facebook.com"
    url_template = "https://www.facebook.com/{username}"


class LinkedInPlugin(_Blocking):
    name = "LinkedIn"
    domain = "linkedin.com"
    url_template = "https://www.linkedin.com/in/{username}"


class TikTokPlugin(_Blocking):
    name = "TikTok"
    domain = "tiktok.com"
    url_template = "https://www.tiktok.com/@{username}"


class ThreadsPlugin(_Blocking):
    name = "Threads"
    domain = "threads.net"
    url_template = "https://www.threads.net/@{username}"


class TwitchPlugin(_Blocking):
    name = "Twitch"
    domain = "twitch.tv"
    url_template = "https://www.twitch.tv/{username}"
