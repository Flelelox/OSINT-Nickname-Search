from __future__ import annotations

import asyncio

from PySide6.QtCore import QThread, Signal

from search.engine import SearchEngine


class SearchWorker(QThread):
    """
    Выполняет поиск в отдельном потоке, чтобы не блокировать GUI.
    """

    results_ready = Signal(list)
    error = Signal(str)
    progress = Signal(int, int)  # (сделано, всего)

    def __init__(
        self,
        nickname: str,
        threshold: int = 80,
        search_similar: bool = True,
        enabled_services: list[str] | None = None,
    ):
        super().__init__()
        self.nickname = nickname
        self.threshold = threshold
        self.search_similar = search_similar
        self.enabled_services = enabled_services

    def run(self):
        try:
            engine = SearchEngine(self.enabled_services)

            results = asyncio.run(
                engine.search(
                    self.nickname,
                    threshold=self.threshold,
                    search_similar=self.search_similar,
                    progress=self._on_progress,
                )
            )

            self.results_ready.emit(results)

        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))

    def _on_progress(self, done: int, total: int) -> None:
        # Qt-сигналы потокобезопасны для emit.
        self.progress.emit(done, total)
