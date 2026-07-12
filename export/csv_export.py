from __future__ import annotations

import csv
from pathlib import Path

from core.models import SearchResult


class CsvExporter:

    @staticmethod
    def export(
        results: list[SearchResult],
        path: str | Path,
        meta: dict | None = None,
    ):

        with open(path, "w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Service",
                "Username",
                "Display Name",
                "Profile URL",
                "Similarity",
                "Confidence",
                "Group",
                "Followers",
                "Website",
                "Source",
                "Exists",
            ])

            for r in results:

                writer.writerow([
                    r.service,
                    r.username,
                    r.display_name,
                    r.profile_url,
                    r.similarity,
                    r.identity_score,
                    (r.identity_group + 1) if r.identity_group >= 0 else "",
                    r.followers,
                    r.website,
                    r.source,
                    int(r.exists),
                ])
