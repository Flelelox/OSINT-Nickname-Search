from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from core.models import SearchResult


class JsonExporter:

    @staticmethod
    def export(
        results: list[SearchResult],
        path: str | Path,
        meta: dict | None = None,
    ):

        items = [asdict(result) for result in results]

        # Если переданы метаданные поиска — заворачиваем в объект,
        # иначе сохраняем плоский список (обратная совместимость).
        if meta:
            payload = {**meta, "count": len(items), "results": items}
        else:
            payload = items

        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4, ensure_ascii=False)
