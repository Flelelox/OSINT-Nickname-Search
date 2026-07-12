"""
Парсер результатов поисковых систем.
"""

from __future__ import annotations

from bs4 import BeautifulSoup


class SearchParser:

    @staticmethod
    def extract_links(html: str) -> list[str]:

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        links = []

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if href.startswith("http"):

                links.append(href)

        return list(dict.fromkeys(links))