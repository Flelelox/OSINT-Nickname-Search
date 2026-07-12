from __future__ import annotations

import html as _html
from pathlib import Path

from core.models import SearchResult


class HtmlExporter:

    @staticmethod
    def export(
        results: list[SearchResult],
        path: str | Path,
        meta: dict | None = None,
    ) -> None:

        meta = meta or {}

        def esc(value) -> str:
            return _html.escape(str(value)) if value is not None else "-"

        head = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OSINT Nickname Search Report</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,Helvetica,sans-serif;}
body{background:#0d1117;color:#fff;padding:40px;}
.container{max-width:1100px;margin:auto;}
.header{margin-bottom:30px;}
.header h1{font-size:34px;margin-bottom:10px;}
.meta{color:#8b949e;line-height:1.8;}
.author{margin-top:14px;color:#58a6ff;font-weight:bold;}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;
      padding:20px;margin-bottom:18px;}
.card:hover{border-color:#58a6ff;}
.service{font-size:21px;font-weight:bold;margin-bottom:12px;}
.row{margin:6px 0;color:#d0d7de;}
.row b{color:#fff;}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;
       font-size:12px;font-weight:bold;margin-left:6px;}
.sim{background:#1f6feb33;color:#58a6ff;}
.conf{background:#23863633;color:#3fb950;}
.grp{background:#8957e533;color:#a371f7;}
a{color:#58a6ff;text-decoration:none;}
a:hover{text-decoration:underline;}
.footer{margin-top:50px;padding-top:20px;border-top:1px solid #30363d;
        text-align:center;color:#8b949e;line-height:1.8;}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>OSINT Nickname Search Report</h1>
<div class="meta">
"""

        head += f"Никнейм: <b>{esc(meta.get('query', '-'))}</b><br>"
        head += f"Найдено профилей: <b>{len(results)}</b><br>"
        if meta.get("elapsed") is not None:
            head += f"Время поиска: <b>{meta['elapsed']:.1f} с</b><br>"
        if meta.get("generated"):
            head += f"Сформировано: <b>{esc(meta['generated'])}</b><br>"

        head += """
</div>
<div class="author">Developed by <b>flelelox</b></div>
</div>
"""

        cards = []
        for r in results:
            group = (r.identity_group + 1) if r.identity_group >= 0 else "-"
            cards.append(f"""
<div class="card">
<div class="service">{esc(r.service)}
<span class="badge sim">похоже {r.similarity:.0f}%</span>
<span class="badge conf">увер. {r.identity_score:.0f}%</span>
<span class="badge grp">группа {group}</span>
</div>
<div class="row"><b>Никнейм:</b> {esc(r.username)}</div>
<div class="row"><b>Имя:</b> {esc(r.display_name)}</div>
<div class="row"><b>Описание:</b> {esc(r.biography)}</div>
<div class="row"><b>Подписчики:</b> {esc(r.followers)}</div>
<div class="row"><b>Сайт:</b> {esc(r.website)}</div>
<div class="row"><b>Источник:</b> {esc(r.source)}</div>
<div class="row"><b>Профиль:</b>
<a href="{esc(r.profile_url)}">{esc(r.profile_url)}</a></div>
</div>
""")

        footer = """
<div class="footer">
<b>OSINT Nickname Search</b><br>
Developed by <b>flelelox</b><br>
Open Source Intelligence • Поиск по открытым источникам
</div>
</div>
</body>
</html>
"""

        Path(path).write_text(head + "".join(cards) + footer, encoding="utf-8")
