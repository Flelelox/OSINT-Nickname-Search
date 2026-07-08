from __future__ import annotations

from pathlib import Path

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from core.models import SearchResult


class PdfExporter:

    @staticmethod
    def export(
        results: list[SearchResult],
        path: str | Path,
        meta: dict | None = None,
    ) -> None:

        meta = meta or {}

        doc = SimpleDocTemplate(str(path))
        styles = getSampleStyleSheet()
        elements = []

        elements.append(
            Paragraph("<b>OSINT Nickname Search Report</b>", styles["Heading1"])
        )
        elements.append(
            Paragraph("Developed by <b>flelelox</b>", styles["Normal"])
        )

        if meta.get("query"):
            elements.append(
                Paragraph(f"Никнейм: <b>{meta['query']}</b>", styles["Normal"])
            )
        elements.append(
            Paragraph(f"Найдено профилей: <b>{len(results)}</b>", styles["Normal"])
        )
        if meta.get("elapsed") is not None:
            elements.append(
                Paragraph(
                    f"Время поиска: <b>{meta['elapsed']:.1f} с</b>",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 20))

        for r in results:
            group = (r.identity_group + 1) if r.identity_group >= 0 else "-"

            elements.append(
                Paragraph(f"<b>Сервис:</b> {r.service}", styles["Heading2"])
            )
            elements.append(
                Paragraph(f"<b>Никнейм:</b> {r.username or '-'}", styles["BodyText"])
            )
            elements.append(
                Paragraph(f"<b>Имя:</b> {r.display_name or '-'}", styles["BodyText"])
            )
            elements.append(
                Paragraph(
                    f"<b>Похоже:</b> {r.similarity:.0f}% &nbsp; "
                    f"<b>Уверенность:</b> {r.identity_score:.0f}% &nbsp; "
                    f"<b>Группа:</b> {group}",
                    styles["BodyText"],
                )
            )
            elements.append(
                Paragraph(f"<b>Подписчики:</b> {r.followers or '-'}", styles["BodyText"])
            )
            elements.append(
                Paragraph(f"<b>Источник:</b> {r.source}", styles["BodyText"])
            )
            elements.append(
                Paragraph(f"<b>Профиль:</b> {r.profile_url or '-'}", styles["BodyText"])
            )
            elements.append(Spacer(1, 16))

        doc.build(elements)
