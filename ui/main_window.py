from __future__ import annotations

import time

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices, QColor
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
    QFrame,
    QWidgetAction,
    QSizePolicy,
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
        self.resize(1440, 880)

        self.results: list[SearchResult] = []
        self.worker: SearchWorker | None = None
        self.started_at: float = 0.0
        self.last_meta: dict = {}
        self.service_checks: dict[str, QCheckBox] = {}

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
        self.layout.setContentsMargins(24, 20, 24, 20)
        self.layout.setSpacing(14)
        central.setLayout(self.layout)

        self.setStyleSheet(_STYLE)

        # --- заголовок ---
        header = QVBoxLayout()
        header.setSpacing(2)

        title = QLabel("OSINT Nickname Search")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 23, QFont.Bold))
        header.addWidget(title)

        author = QLabel("Developed by flelelox")
        author.setAlignment(Qt.AlignCenter)
        author.setObjectName("author")
        header.addWidget(author)

        self.layout.addLayout(header)

        # --- панель поиска (карточка) ---
        search_card = QFrame()
        search_card.setObjectName("card")
        search_card_layout = QVBoxLayout(search_card)
        search_card_layout.setContentsMargins(16, 16, 16, 16)
        search_card_layout.setSpacing(12)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.nickname = QLineEdit()
        self.nickname.setPlaceholderText("Введите никнейм...")
        self.nickname.setMinimumHeight(40)
        search_layout.addWidget(self.nickname, stretch=1)

        self.search_button = QPushButton("🔍  Поиск")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setMinimumHeight(40)
        self.search_button.setMinimumWidth(130)
        search_layout.addWidget(self.search_button)

        search_card_layout.addLayout(search_layout)

        # --- панель настроек ---
        options = QHBoxLayout()
        options.setSpacing(16)

        threshold_box = QHBoxLayout()
        threshold_box.setSpacing(6)
        threshold_box.addWidget(QLabel("Порог совпадения:"))
        self.threshold = QSpinBox()
        self.threshold.setRange(50, 100)
        self.threshold.setValue(80)
        self.threshold.setSuffix(" %")
        self.threshold.setFixedWidth(90)
        threshold_box.addWidget(self.threshold)
        options.addLayout(threshold_box)

        self.similar_check = QCheckBox("Искать похожие ники")
        self.similar_check.setChecked(True)
        options.addWidget(self.similar_check)

        options.addStretch(1)

        self.services_button = QPushButton()
        self.services_button.setObjectName("secondaryButton")
        self.services_menu = QMenu(self)
        self._build_services_menu()
        self.services_button.setMenu(self.services_menu)
        options.addWidget(self.services_button)

        search_card_layout.addLayout(options)

        self.layout.addWidget(search_card)

        # --- прогресс ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
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
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.cellDoubleClicked.connect(self.open_profile)
        self.layout.addWidget(self.table, stretch=1)

        # --- нижняя панель: экспорт + лог ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)
        export_label = QLabel("Экспорт:")
        export_label.setObjectName("mutedLabel")
        bottom_row.addWidget(export_label)

        self.export_json = QPushButton("JSON")
        self.export_csv = QPushButton("CSV")
        self.export_html = QPushButton("HTML")
        self.export_pdf = QPushButton("PDF")
        for btn in (self.export_json, self.export_csv,
                    self.export_html, self.export_pdf):
            btn.setObjectName("exportButton")
            btn.setMinimumWidth(80)
            bottom_row.addWidget(btn)

        bottom_row.addStretch(1)
        self.layout.addLayout(bottom_row)

        # --- лог ---
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(130)
        self.layout.addWidget(self.log)

    # ------------------------------------------------------------
    # Меню выбора сервисов: не закрывается при отметке чекбоксов,
    # т.к. чекбоксы находятся внутри QWidgetAction, а не являются
    # обычными checkable QAction (которые Qt закрывает по клику).
    # ------------------------------------------------------------

    def _build_services_menu(self):
        self.services_menu.setMinimumWidth(240)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(12, 10, 12, 10)
        vbox.setSpacing(6)

        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("Сервисы"))
        header_row.addStretch(1)

        select_all_btn = QPushButton("Все")
        select_all_btn.setObjectName("menuLinkButton")
        select_none_btn = QPushButton("Нет")
        select_none_btn.setObjectName("menuLinkButton")
        header_row.addWidget(select_all_btn)
        header_row.addWidget(select_none_btn)
        vbox.addLayout(header_row)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("menuSeparator")
        vbox.addWidget(line)

        for name, enabled, reliable in self.available_services:
            label = name if reliable else f"{name} (ненадёжно)"
            cb = QCheckBox(label)
            cb.setChecked(enabled)
            cb.toggled.connect(self._update_services_button_label)
            vbox.addWidget(cb)
            self.service_checks[name] = cb

        if not self.available_services:
            empty = QLabel("Сервисы не найдены")
            empty.setObjectName("mutedLabel")
            vbox.addWidget(empty)

        select_all_btn.clicked.connect(
            lambda: [cb.setChecked(True) for cb in self.service_checks.values()]
        )
        select_none_btn.clicked.connect(
            lambda: [cb.setChecked(False) for cb in self.service_checks.values()]
        )

        widget_action = QWidgetAction(self.services_menu)
        widget_action.setDefaultWidget(container)
        self.services_menu.addAction(widget_action)

        self._update_services_button_label()

    def _update_services_button_label(self):
        total = len(self.service_checks)
        checked = sum(cb.isChecked() for cb in self.service_checks.values())
        self.services_button.setText(f"Сервисы ({checked}/{total}) ▾")

    def _selected_services(self) -> list[str]:
        return [
            name for name, cb in self.service_checks.items()
            if cb.isChecked()
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
QMainWindow{ background:#0f1521; }
QWidget{ background:#0f1521; color:#e5e7eb; font-size:13px; }
QLabel{ color:#e5e7eb; }
QLabel#author{ color:#60a5fa; font-size:12px; }
QLabel#mutedLabel{ color:#9ca3af; font-size:12px; }

QFrame#card{
    background:#161d2c; border:1px solid #26304544;
    border-radius:12px;
}

QLineEdit{
    background:#1c2438; border:1px solid #2c3752;
    border-radius:9px; padding:9px 12px; selection-background-color:#2563eb;
}
QLineEdit:focus{ border:1px solid #3b82f6; }

QSpinBox{
    background:#1c2438; border:1px solid #2c3752;
    border-radius:7px; padding:4px 6px;
}
QSpinBox:focus{ border:1px solid #3b82f6; }

QCheckBox{ color:#e5e7eb; spacing:8px; padding:2px 0; }
QCheckBox::indicator{
    width:16px; height:16px; border-radius:4px;
    border:1px solid #3b4761; background:#1c2438;
}
QCheckBox::indicator:checked{
    background:#2563eb; border:1px solid #2563eb;
}

/* Основная кнопка (Поиск) */
QPushButton#primaryButton{
    background:#2563eb; border:none; border-radius:9px;
    padding:9px 18px; color:white; font-weight:600;
}
QPushButton#primaryButton:hover{ background:#3b82f6; }
QPushButton#primaryButton:pressed{ background:#1d4ed8; }
QPushButton#primaryButton:disabled{ background:#2c3752; color:#7b869c; }

/* Второстепенная кнопка (Сервисы) */
QPushButton#secondaryButton{
    background:#1c2438; border:1px solid #2c3752; border-radius:9px;
    padding:9px 14px; color:#e5e7eb;
}
QPushButton#secondaryButton:hover{ background:#232c45; border:1px solid #3b4761; }
QPushButton#secondaryButton::menu-indicator{ image:none; width:0; }

/* Кнопки экспорта — компактные и приглушённые */
QPushButton#exportButton{
    background:transparent; border:1px solid #2c3752; border-radius:8px;
    padding:6px 12px; color:#cbd5e1; font-size:12px;
}
QPushButton#exportButton:hover{ background:#1c2438; border:1px solid #3b4761; color:white; }
QPushButton#exportButton:pressed{ background:#161d2c; }

/* Ссылки внутри меню сервисов */
QPushButton#menuLinkButton{
    background:transparent; border:none; color:#60a5fa;
    padding:2px 6px; font-size:12px;
}
QPushButton#menuLinkButton:hover{ color:#93c5fd; text-decoration:underline; }

QFrame#menuSeparator{ background:#2c3752; max-height:1px; }

QMenu{
    background:#161d2c; color:#e5e7eb; border:1px solid #2c3752;
    border-radius:10px; padding:4px;
}

QTableWidget{
    background:#161d2c; border:1px solid #26304544;
    border-radius:10px; gridline-color:#232c45;
    alternate-background-color:#1a2233;
}
QTableWidget::item{ padding:4px; }
QTableWidget::item:selected{ background:#26406b; }
QHeaderView::section{
    background:#1c2438; color:#cbd5e1; border:0px;
    border-bottom:1px solid #2c3752; padding:8px 6px; font-weight:600;
}

QTextEdit{
    background:#161d2c; border:1px solid #26304544; border-radius:10px;
    padding:6px; color:#cbd5e1;
}

QProgressBar{
    background:#1c2438; border:none; border-radius:3px;
}
QProgressBar::chunk{ background:#2563eb; border-radius:3px; }

QScrollBar:vertical{
    background:transparent; width:10px; margin:0;
}
QScrollBar::handle:vertical{
    background:#2c3752; border-radius:5px; min-height:24px;
}
QScrollBar::handle:vertical:hover{ background:#3b4761; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical{ height:0; }
"""
