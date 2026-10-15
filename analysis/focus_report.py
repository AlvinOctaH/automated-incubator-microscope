#!/usr/bin/env python3
"""
Focus Validation Report Generator (Sharpness Only)
"""

import sys
import os
import csv
import json
import math
import glob
from datetime import datetime


# ============================
# LOAD CSV
# ============================

def load_csv(path):

    rows = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append({
                "cycle": int(row["cycle"]),
                "timestamp": row["timestamp"],
                "sharpness": float(row["sharpness"]),
                "image_path": row["image_path"],
            })

    return rows


# ============================
# STATISTICS
# ============================

def stats(values):

    n = len(values)

    mean = sum(values) / n

    std = math.sqrt(sum((v - mean) ** 2 for v in values) / n)

    mn = min(values)
    mx = max(values)

    cv = (std / mean * 100) if mean else 0

    return {
        "mean": mean,
        "std": std,
        "min": mn,
        "max": mx,
        "range": mx - mn,
        "cv": cv,
    }


# ============================
# IMAGE ENCODER
# ============================

def encode_image(path):

    import base64

    if os.path.exists(path):

        with open(path, "rb") as f:
            return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

    return ""


# ============================
# BUILD HTML REPORT
# ============================

def build_html(rows, csv_filename):

    sharp_vals = [r["sharpness"] for r in rows]
    cycles = [r["cycle"] for r in rows]

    s = stats(sharp_vals)

    def cv_label(cv):

        if cv < 2:
            return "EXCELLENT"
        elif cv < 5:
            return "GOOD"
        elif cv < 10:
            return "ACCEPTABLE"
        else:
            return "POOR"

    gallery_html = ""

    for r in rows:

        img = encode_image(r["image_path"])

        if img:
            img_tag = f'<img src="{img}" style="width:100%;border-radius:6px;">'
        else:
            img_tag = '<div style="height:80px;background:#eee;border-radius:6px;"></div>'

        gallery_html += f"""
        <div style="background:#fff;border:1px solid #ddd;border-radius:10px;padding:10px;font-size:12px;">
            {img_tag}
            <div style="margin-top:6px;font-weight:600;">Cycle {r['cycle']}</div>
            <div>Sharpness: <b>{r['sharpness']:.4f}</b></div>
        </div>
        """

    chart_data = json.dumps({
        "cycles": cycles,
        "sharp": sharp_vals
    })

    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<title>Focus Repeatability Report</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>

<style>

body {{
font-family: system-ui;
background:#f5f5f5;
margin:0;
}}

.header {{
background:#1a1a2e;
color:white;
padding:30px;
}}

.container {{
max-width:1000px;
margin:auto;
padding:30px;
}}

.metric-grid {{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
gap:14px;
margin-bottom:30px;
}}

.metric {{
background:white;
padding:20px;
border-radius:10px;
border:1px solid #e8e8e8;
}}

.metric-label {{
font-size:12px;
color:#888;
}}

.metric-value {{
font-size:28px;
font-weight:700;
}}

.section {{
background:white;
padding:20px;
border-radius:10px;
border:1px solid #e8e8e8;
margin-bottom:25px;
}}

.chart-wrap {{
height:250px;
}}

.gallery {{
display:grid;
grid-template-columns:repeat(auto-fill,minmax(150px,1fr));
gap:12px;
}}

table {{
width:100%;
border-collapse:collapse;
}}

th,td {{
padding:8px;
border-top:1px solid #eee;
text-align:left;
}}

</style>

</head>

<body>

<div class="header">

<h1>Z-Axis Focus Repeatability Report</h1>

<p>Source: {csv_filename} | Generated: {generated}</p>

</div>


<div class="container">

<div class="metric-grid">

<div class="metric">
<div class="metric-label">Mean sharpness</div>
<div class="metric-value">{s['mean']:.4f}</div>
</div>

<div class="metric">
<div class="metric-label">Standard deviation</div>
<div class="metric-value">{s['std']:.4f}</div>
</div>

<div class="metric">
<div class="metric-label">Coefficient of variation</div>
<div class="metric-value">{s['cv']:.2f}%</div>
<div style="font-size:12px;color:#888;">{cv_label(s['cv'])}</div>
</div>

<div class="metric">
<div class="metric-label">Minimum sharpness</div>
<div class="metric-value">{s['min']:.4f}</div>
</div>

<div class="metric">
<div class="metric-label">Maximum sharpness</div>
<div class="metric-value">{s['max']:.4f}</div>
</div>

<div class="metric">
<div class="metric-label">Cycles tested</div>
<div class="metric-value">{len(rows)}</div>
</div>

</div>


<div class="section">

<h2>Sharpness per cycle</h2>

<div class="chart-wrap">

<canvas id="sharpChart"></canvas>

</div>

</div>


<div class="section">

<h2>Raw sharpness data</h2>

<table>

<tr>
<th>Cycle</th>
<th>Sharpness</th>
</tr>

{''.join(f"<tr><td>{r['cycle']}</td><td>{r['sharpness']:.4f}</td></tr>" for r in rows)}

</table>

</div>


<div class="section">

<h2>Image gallery</h2>

<div class="gallery">

{gallery_html}

</div>

</div>

</div>


<script>

const D = {chart_data};

new Chart(document.getElementById("sharpChart"), {{

type: "line",

data: {{

labels: D.cycles,

datasets: [{{
label: "Sharpness",
data: D.sharp,
borderWidth:2,
tension:0.3
}}]

}},

options: {{
responsive:true,
maintainAspectRatio:false
}}

}});

</script>

</body>
</html>
"""

    return html


# ============================
# MAIN
# ============================

def main():

    if len(sys.argv) > 1:

        csv_path = sys.argv[1]

    else:

        files = sorted(glob.glob("focus_results_*.csv"))

        if not files:
            print("No CSV found")
            sys.exit(1)

        csv_path = files[-1]

    rows = load_csv(csv_path)

    html = build_html(rows, os.path.basename(csv_path))

    out_name = f"focus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    with open(out_name, "w") as f:
        f.write(html)

    print("Report created:", out_name)


if __name__ == "__main__":
    main()