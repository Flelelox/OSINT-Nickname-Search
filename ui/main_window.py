from __future__ import annotations

import time

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices, QAction, QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QHeaderView,
    QFileDialog,
    QMessageBox,
    QSpinBox,
    QCheckBox,
    QMenu,
)

from core.models import SearchResult
from search.engine import SearchEngine
from ui.search_worker import SearchWorker
from export.json_export import JsonExporter
from export.csv_export import CsvExporter
from export.html_export import HtmlExporter
from export.pdf_export import PdfExporter

# Цвета для подсветки групп корреляции.
_GROUP_COLORS = [
    "#1e3a8a", "#065f46", "#7c2d12", "#4c1d95",
    "#155e75", "#854d0e", "#831843", "#3f3f46",
]


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OSINT Nickname Search")
        self.resize(1400, 860)

        self.results: list[SearchResult] = []
        self.worker: SearchWorker | None = None
        self.started_at: float = 0.0
        self.last_meta: dict = {}

        # Список сервисов для меню выбора (имя, включён, надёжен).
        try:
            self.available_services = SearchEngine().services()
        except Exception:
            self.available_services = []

        self.build_ui()

        self.search_button.clicked.connect(self.search)
        self.nickname.returnPressed.connect(self.search)

        self.export_json.clicked.connect(self.on_export_json)
        self.export_csv.clicked.connect(self.on_export_csv)
        self.export_html.clicked.connect(self.on_export_html)
        self.export_pdf.clicked.connect(self.on_export_pdf)

    # ==========================================================
    # Построение интерфейса
    # ==========================================================

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        central.setLayout(self.layout)

        self.setStyleSheet(_STYLE)

        title = QLabel("OSINT Nickname Search")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.layout.addWidget(title)

        author = QLabel("Developed by flelelox")
        author.setAlignment(Qt.AlignCenter)
        author.setStyleSheet("color:#60a5fa;font-size:13px;")
        self.layout.addWidget(author)

        # --- строка поиска ---
        search_layout = QHBoxLayout()

        self.nickname = QLineEdit()
        self.nickname.setPlaceholderText("Введите никнейм...")
        search_layout.addWidget(self.nickname, stretch=1)

        self.search_button = QPushButton("Поиск")
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        # --- панель настроек ---
        options = QHBoxLayout()

        options.addWidget(QLabel("Порог совпадения:"))

        self.threshold = QSpinBox()
        self.threshold.setRange(50, 100)
        self.threshold.setValue(80)
        self.threshold.setSuffix(" %")
        self.threshold.setFixedWidth(90)
        options.addWidget(self.threshold)

        self.similar_check = QCheckBox("Искать похожие ники")
        self.similar_check.setChecked(True)
        options.addWidget(self.similar_check)

        self.services_button = QPushButton("Сервисы ▾")
        self.services_menu = QMenu(self)
        self.service_actions: dict[str, QAction] = {}
        self._build_services_menu()
        self.services_button.setMenu(self.services_menu)
        options.addWidget(self.services_button)

        options.addStretch(1)
        self.layout.addLayout(options)

        # --- прогресс ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.layout.addWidget(self.progress)

        # --- таблица ---
        self.columns = [
            "Сервис", "Никнейм", "Имя",
            "Похоже %", "Увер. %", "Группа",
            "Подписчики", "Профиль",
        ]
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self.open_profile)
        self.layout.addWidget(self.table, stretch=1)

        # --- экспорт ---
        export_layout = QHBoxLayout()
        self.export_json = QPushButton("Экспорт JSON")
        self.export_csv = QPushButton("Экспорт CSV")
        self.export_html = QPushButton("Экспорт HTML")
        self.export_pdf = QPushButton("Экспорт PDF")
        for btn in (self.export_json, self.export_csv,
                    self.export_html, self.export_pdf):
            export_layout.addWidget(btn)
        self.layout.addLayout(export_layout)

        # --- лог ---
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        self.layout.addWidget(self.log)

    def _build_services_menu(self):
        for name, enabled, reliable in self.available_services:
            label = name if reliable else f"{name} (ненадёжно)"
            action = QAction(label, self, checkable=True)
            action.setChecked(enabled)
            self.services_menu.addAction(action)
            self.service_actions[name] = action

    def _selected_services(self) -> list[str]:
        return [
            name for name, action in self.service_actions.items()
            if action.isChecked()
        ]

    # ==========================================================
    # Поиск
    # ==========================================================

    def search(self):
        nickname = self.nickname.text().strip()

        if not nickname:
            self.log.append("Введите никнейм.")
            return

        if self.worker is not None and self.worker.isRunning():
            self.log.append("Поиск уже выполняется...")
            return

        services = self._selected_services()
        if not services:
            self.log.append("Не выбрано ни одного сервиса.")
            return

        self.log.clear()
        self.log.append(f"Начинаю поиск: {nickname}")
        self.log.append(
            f"Сервисов: {len(services)} | "
            f"порог: {self.threshold.value()}% | "
            f"похожие ники: {'да' if self.similar_check.isChecked() else 'нет'}"
        )

        self.results = []
        self.table.setRowCount(0)
        self.progress.setRange(0, 0)  # индикатор занятости, пока не знаем total
        self.progress.setValue(0)
        self.search_button.setEnabled(False)
        self.started_at = time.time()

        self.worker = SearchWorker(
            nickname,
            threshold=self.threshold.value(),
            search_similar=self.similar_check.isChecked(),
            enabled_services=services,
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.results_ready.connect(self.on_results)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, done: int, total: int):
        if total <= 0:
            return
        if self.progress.maximum() != total:
            self.progress.setRange(0, total)
        self.progress.setValue(done)

    def on_results(self, results: list[SearchResult]):
        self.results = results

        self.progress.setRange(0, 100)
        self.progress.setValue(100)

        self.populate_table(results)

        elapsed = time.time() - self.started_at
        groups = len({r.identity_group for r in results if r.identity_group >= 0})

        self.last_meta = {
            "query": self.nickname.text().strip(),
            "elapsed": elapsed,
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.log.append(f"Найдено профилей: {len(results)}")
        self.log.append(f"Групп (вероятных личностей): {groups}")
        self.log.append(f"Время поиска: {elapsed:.1f} с")
        self.log.append("Поиск завершён.")

        self.finish_thread()

    def on_error(self, message: str):
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.log.append(f"Ошибка: {message}")
        self.finish_thread()

    def finish_thread(self):
        self.search_button.setEnabled(True)
        if self.worker is not None:
            self.worker.wait()
            self.worker = None

    def populate_table(self, results: list[SearchResult]):
        self.table.setRowCount(len(results))

        for row, r in enumerate(results):
            group_label = str(r.identity_group + 1) if r.identity_group >= 0 else "-"

            values = [
                r.service,
                r.username or "-",
                r.display_name or "-",
                f"{r.similarity:.0f}",
                f"{r.identity_score:.0f}",
                group_label,
                str(r.followers) if r.followers is not None else "-",
                r.profile_url or "-",
            ]

            color = None
            if r.identity_group >= 0:
                color = QColor(_GROUP_COLORS[r.identity_group % len(_GROUP_COLORS)])

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if color is not None:
                    item.setBackground(color)
                self.table.setItem(row, col, item)

    def open_profile(self, row: int, column: int):
        if 0 <= row < len(self.results):
            url = self.results[row].profile_url
            if url:
                QDesktopServices.openUrl(QUrl(url))

    # ==========================================================
    # Экспорт
    # ==========================================================

    def _run_export(self, exporter, default_name: str, file_filter: str):
        if not self.results:
            self.log.append("Нет данных для экспорта. Сначала выполните поиск.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", default_name, file_filter
        )
        if not path:
            return

        try:
            exporter.export(self.results, path, self.last_meta)
            self.log.append(f"Экспортировано: {path}")
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Ошибка экспорта", str(e))
            self.log.append(f"Ошибка экспорта: {e}")

    def on_export_json(self):
        self._run_export(JsonExporter, "results.json", "JSON (*.json)")

    def on_export_csv(self):
        self._run_export(CsvExporter, "results.csv", "CSV (*.csv)")

    def on_export_html(self):
        self._run_export(HtmlExporter, "report.html", "HTML (*.html)")

    def on_export_pdf(self):
        self._run_export(PdfExporter, "report.pdf", "PDF (*.pdf)")


_STYLE = """
QMainWindow{ background:#111827; }
QWidget{ background:#111827; color:white; font-size:13px; }
QLabel{ color:white; }
QLineEdit{
    background:#1f2937; border:1px solid #374151;
    border-radius:8px; padding:10px;
}
QSpinBox{
    background:#1f2937; border:1px solid #374151;
    border-radius:6px; padding:4px;
}
QCheckBox{ color:white; }
QPushButton{
    background:#2563eb; border:none; border-radius:8px;
    padding:9px 16px; color:white;
}
QPushButton:hover{ background:#1d4ed8; }
QPushButton:disabled{ background:#374151; color:#9ca3af; }
QMenu{ background:#1f2937; color:white; border:1px solid #374151; }
QMenu::item:selected{ background:#2563eb; }
QTableWidget{
    background:#1f2937; border:1px solid #374151;
    gridline-color:#374151;
}
QHeaderView::section{
    background:#1f2937; color:white; border:0px;
    border-bottom:1px solid #374151; padding:6px;
}
QTextEdit{ background:#1f2937; border:1px solid #374151; }
QProgressBar{
    background:#1f2937; border:1px solid #374151;
    border-radius:8px; text-align:center;
}
QProgressBar::chunk{ background:#2563eb; border-radius:8px; }
"""
