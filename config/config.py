"""
Загрузка конфигурации проекта.
"""

from __future__ import annotations

import json
from pathlib import Path


CONFIG_DIR = Path("config")

CONFIG_FILE = CONFIG_DIR / "config.json"


DEFAULT_CONFIG = {

    "max_connections": 20,

    "request_timeout": 15,

    "retry_count": 3,

    "cache_ttl": 600,

    "similarity": 80,

    "theme": "dark",

    "language": "en",

    "user_agent": (

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "

        "AppleWebKit/537.36 (KHTML, like Gecko) "

        "Chrome/138.0 Safari/537.36"

    )

}


class Config:

    def __init__(self):

        CONFIG_DIR.mkdir(exist_ok=True)

        if not CONFIG_FILE.exists():

            self.save(DEFAULT_CONFIG)

        self.data = self.load()

    # ======================================================

    def load(self):

        with open(

            CONFIG_FILE,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(file)

    # ======================================================

    def save(self, data):

        with open(

            CONFIG_FILE,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                data,

                file,

                indent=4,

                ensure_ascii=False

            )

    # ======================================================

    def get(

        self,

        key,

        default=None

    ):

        return self.data.get(

            key,

            default

        )

    # ======================================================

    def set(

        self,

        key,

        value

    ):

        self.data[key] = value

        self.save(self.data)