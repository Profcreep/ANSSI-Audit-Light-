from pathlib import Path
from core.context import get_context
import json
import math
import os
from core.config import REPORTS_DIR

SEVERITY_COLOR = {
    "✅": "#2ecc71",   # vert
    "⚠️": "#f39c12",   # orange
    "❌": "#e74c3c",   # rouge
    "⏳": "#95a5a6"    # gris
}

class Report:
    def __init__(self):
        self.context = get_context()
        self.sections = {}

    def add_section(self, name, results):
        """
        results = list of (status, message, extra)
        """
        self.sections[name] = results

    # ------------------ SCORING ------------------

    def _section_score(self, items):
        ok = warn = fail = 0
        for status, *_ in items:
            if status == "✅":
                ok += 1
            elif status == "⚠️":
                warn += 1
            elif status == "❌":
                fail += 1

        total = ok + warn + fail
        if total == 0:
            return 100

        score = ((ok + 0.5 * warn) / total) * 100
        return round(score, 1)

    def _global_score(self, section_scores):
        if not section_scores:
            return 0
        return round(sum(section_scores.values()) / len(section_scores), 1)

    # ------------------ REPORT ------------------

    def generate(self):
        hostname = self.context["hostname"]
        date = self.context["date"]
        fname_date = self.context["filename_date"]

        # Scores par section
        section_scores = {
            name: self._section_score(items)
            for name, items in self.sections.items()
        }

        global_score = self._global_score(section_scores)
        best_section = max(section_scores, key=section_scores.get)
        worst_section = min(section_scores, key=section_scores.get)

        score_class = (
            "ok" if global_score >= 80
            else "warn" if global_score >= 50
            else "fail"
        )

        # ------------------ HTML ------------------

        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>ANSSI Light Audit - {hostname}</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {{
    font-family: Arial, sans-serif;
    background:#f4f6f8;
    padding:20px;
}}

h1 {{ color:#2c3e50; }}
h2 {{ border-bottom:2px solid #34495e; padding-bottom:4px; }}

.section {{
    background:white;
    padding:15px;
    margin-bottom:20px;
    border-radius:6px;
    box-shadow:0 2px 6px rgba(0,0,0,0.1);
}}

.item {{ margin:4px 0; }}

.ok {{ color:#2ecc71; }}
.warn {{ color:#f39c12; }}
.fail {{ color:#e74c3c; }}

.flex {{
    display:flex;
    gap:20px;
    flex-wrap:wrap;
}}

.chart {{
    width:320px;
}}
</style>
</head>

<body>

<h1>ANSSI – Diagnostic de sécurité (Light+)</h1>

<div class="section">
<b>Machine :</b> {hostname}<br>
<b>Date :</b> {date}
</div>

<div class="section">
<h2>Résumé exécutif</h2>

<p><b>Score global :</b>
<span class="{score_class}">{global_score}%</span>
</p>

<p>🏆 <b>Catégorie la plus conforme :</b>
{best_section} ({section_scores[best_section]}%)
</p>

<p>🚨 <b>Catégorie prioritaire :</b>
{worst_section} ({section_scores[worst_section]}%)
</p>
"""

        # Recommandation automatique
        if section_scores[worst_section] < 50:
            html += f"""
<p><b>Recommandation :</b><br>
La catégorie <b>{worst_section}</b> présente un niveau de non-conformité élevé.
Une action corrective prioritaire est recommandée.</p>
"""
        elif section_scores[worst_section] < 80:
            html += f"""
<p><b>Recommandation :</b><br>
La catégorie <b>{worst_section}</b> est partiellement conforme.
Des améliorations sont recommandées.</p>
"""
        else:
            html += """
<p><b>Recommandation :</b><br>
Le niveau global de conformité est satisfaisant.</p>
"""

        html += "</div>"

        # ------------------ CHARTS ------------------

        labels = list(section_scores.keys())
        scores = list(section_scores.values())

        html += f"""
<div class="section">
<h2>Vue globale</h2>

<div class="flex">
<div class="chart">
<canvas id="globalChart"></canvas>
</div>

<div class="chart">
<canvas id="sectionChart"></canvas>
</div>
</div>

<script>
new Chart(document.getElementById('globalChart'), {{
    type: 'doughnut',
    data: {{
        labels: ['Conforme', 'Non conforme'],
        datasets: [{{
            data: [{global_score}, {100 - global_score}],
            backgroundColor: ['#2ecc71', '#e74c3c']
        }}]
    }}
}});

new Chart(document.getElementById('sectionChart'), {{
    type: 'doughnut',
    data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
            data: {json.dumps(scores)},
            backgroundColor: ['#2ecc71','#3498db','#f39c12','#e74c3c']
        }}]
    }}
}});
</script>
</div>
"""

        # ------------------ DETAILS ------------------

        for section, items in self.sections.items():
            html += f"<div class='section'><h2>{section}</h2>"
            for status, msg, *_ in items:
                color = SEVERITY_COLOR.get(status, "#000")
                html += f"<div class='item' style='color:{color}'>{status} {msg}</div>"
            html += "</div>"

        html += "</body></html>"

        path = REPORTS_DIR / f"{hostname}_{fname_date}.html"
        path.write_text(html, encoding="utf-8")
        return path
