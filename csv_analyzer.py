"""
csv_analyzer.py — Automated CSV Report Generator
Animesh Choubey | github.com/animesh-501

Drop any CSV file in, get a clean HTML report back.
Usage:
    python csv_analyzer.py your_file.csv
    python csv_analyzer.py your_file.csv --output my_report.html
"""

import sys
import os
import argparse
import json
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("Missing dependencies. Run:  pip install pandas numpy")
    sys.exit(1)


# ─── CONFIG ──────────────────────────────────────────────────────────────────

ANOMALY_Z_THRESHOLD = 3.0   # Z-score above which a value is flagged as anomaly
MAX_CATEGORIES      = 10    # Max unique values shown for categorical columns
SAMPLE_ROWS         = 5     # Rows shown in the preview table


# ─── ANALYSIS ────────────────────────────────────────────────────────────────

def load_csv(path: str) -> pd.DataFrame:
    """Load CSV with automatic encoding detection."""
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            print(f"  Loaded '{path}' ({len(df):,} rows × {len(df.columns)} cols) [{enc}]")
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode '{path}' with supported encodings.")


def analyze(df: pd.DataFrame) -> dict:
    """Run full analysis and return a results dict."""
    results = {
        "shape": df.shape,
        "dtypes": {},
        "missing": {},
        "numeric": {},
        "categorical": {},
        "anomalies": [],
        "duplicates": int(df.duplicated().sum()),
    }

    for col in df.columns:
        dtype = str(df[col].dtype)
        results["dtypes"][col] = dtype
        missing = int(df[col].isna().sum())
        results["missing"][col] = {
            "count": missing,
            "pct": round(missing / len(df) * 100, 1)
        }

        # Numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            s = df[col].dropna()
            if len(s) == 0:
                continue
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            results["numeric"][col] = {
                "mean":   round(float(s.mean()), 4),
                "median": round(float(s.median()), 4),
                "std":    round(float(s.std()), 4),
                "min":    round(float(s.min()), 4),
                "max":    round(float(s.max()), 4),
                "q1":     round(float(q1), 4),
                "q3":     round(float(q3), 4),
                "iqr":    round(float(iqr), 4),
                "zeros":  int((s == 0).sum()),
                "negatives": int((s < 0).sum()),
            }

            # Anomaly detection via Z-score
            if s.std() > 0:
                z_scores = np.abs((s - s.mean()) / s.std())
                n_anomalies = int((z_scores > ANOMALY_Z_THRESHOLD).sum())
                if n_anomalies > 0:
                    results["anomalies"].append({
                        "column": col,
                        "count": n_anomalies,
                        "pct": round(n_anomalies / len(s) * 100, 2),
                        "threshold": f"Z > {ANOMALY_Z_THRESHOLD}"
                    })

        # Categorical / object columns
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            vc = df[col].value_counts()
            results["categorical"][col] = {
                "unique":   int(df[col].nunique()),
                "top_vals": {str(k): int(v) for k, v in vc.head(MAX_CATEGORIES).items()},
                "mode":     str(df[col].mode()[0]) if not df[col].mode().empty else "N/A"
            }

    return results


# ─── HTML REPORT ─────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>CSV Report — {filename}</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#080b10;--surface:#0e1318;--border:#1c2530;--accent:#00e5a0;--accent2:#0084ff;--text:#e8edf2;--muted:#5a6a7a;--warn:#f59e0b;--danger:#ff4d6a}}
body{{background:var(--bg);color:var(--text);font-family:'DM Mono',monospace;font-size:0.83rem;padding:2.5rem;line-height:1.7}}
h1{{font-family:'Syne',sans-serif;font-weight:800;font-size:2rem;margin-bottom:0.3rem}}
.meta{{color:var(--muted);font-size:0.75rem;margin-bottom:2.5rem}}
h2{{font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;margin:2.5rem 0 1rem;color:var(--accent);letter-spacing:0.04em}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:0.8rem;margin-bottom:1.5rem}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:1rem 1.2rem}}
.card-label{{font-size:0.68rem;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.4rem}}
.card-val{{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:var(--accent);line-height:1}}
.card-val.warn{{color:var(--warn)}} .card-val.danger{{color:var(--danger)}}
table{{width:100%;border-collapse:collapse;margin-bottom:1.5rem;font-size:0.8rem}}
th{{text-align:left;color:var(--muted);font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;padding:0.4rem 0.8rem;border-bottom:1px solid var(--border)}}
td{{padding:0.5rem 0.8rem;border-bottom:1px solid rgba(28,37,48,0.5);color:var(--muted)}}
td:first-child{{color:var(--text)}}
tr:hover td{{background:rgba(14,19,24,0.8)}}
.pill{{display:inline-block;padding:0.15rem 0.5rem;border-radius:2px;font-size:0.68rem}}
.pill.ok{{background:rgba(0,229,160,0.1);color:var(--accent)}}
.pill.warn{{background:rgba(245,158,11,0.1);color:var(--warn)}}
.pill.bad{{background:rgba(255,77,106,0.1);color:var(--danger)}}
.anomaly-box{{background:rgba(245,158,11,0.05);border:1px solid rgba(245,158,11,0.2);border-radius:4px;padding:1rem 1.2rem;margin-bottom:0.6rem}}
.anomaly-box strong{{color:var(--warn)}}
.col-section{{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:1.2rem 1.5rem;margin-bottom:0.8rem}}
.col-name{{font-family:'Syne',sans-serif;font-weight:700;font-size:0.95rem;margin-bottom:0.8rem}}
.stat-row{{display:flex;flex-wrap:wrap;gap:1.5rem}}
.stat{{display:flex;flex-direction:column}}
.stat-k{{font-size:0.68rem;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase}}
.stat-v{{font-size:0.95rem;color:var(--text)}}
.bar-wrap{{height:8px;background:var(--border);border-radius:2px;margin-top:4px;overflow:hidden}}
.bar{{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:2px;transition:width 0.4s}}
footer{{margin-top:3rem;color:var(--muted);font-size:0.72rem;border-top:1px solid var(--border);padding-top:1rem}}
</style>
</head>
<body>
<h1>📊 CSV Analysis Report</h1>
<div class="meta">File: <strong style="color:var(--text)">{filename}</strong> &nbsp;·&nbsp; Generated: {timestamp} &nbsp;·&nbsp; by csv_analyzer.py</div>

<h2>// Overview</h2>
<div class="grid">
  <div class="card"><div class="card-label">Rows</div><div class="card-val">{rows}</div></div>
  <div class="card"><div class="card-label">Columns</div><div class="card-val">{cols}</div></div>
  <div class="card"><div class="card-label">Numeric Cols</div><div class="card-val" style="color:var(--accent2)">{numeric_count}</div></div>
  <div class="card"><div class="card-label">Categorical Cols</div><div class="card-val" style="color:#a855f7">{categorical_count}</div></div>
  <div class="card"><div class="card-label">Duplicate Rows</div><div class="card-val {dup_class}">{duplicates}</div></div>
  <div class="card"><div class="card-label">Anomaly Flags</div><div class="card-val {anom_class}">{anomaly_count}</div></div>
</div>

<h2>// Missing Values</h2>
{missing_table}

{anomaly_section}

<h2>// Numeric Columns</h2>
{numeric_section}

<h2>// Categorical Columns</h2>
{categorical_section}

<h2>// Data Preview (first {sample_rows} rows)</h2>
{preview_table}

<footer>Generated by csv_analyzer.py — Animesh Choubey · github.com/animesh-501</footer>
</body></html>"""


def missing_table_html(missing: dict) -> str:
    rows_html = ""
    for col, info in sorted(missing.items(), key=lambda x: -x[1]["pct"]):
        pct = info["pct"]
        badge_class = "bad" if pct > 20 else ("warn" if pct > 5 else "ok")
        label = "High" if pct > 20 else ("Medium" if pct > 5 else "OK"  )
        bar = f'<div class="bar-wrap"><div class="bar" style="width:{min(pct,100)}%"></div></div>'
        rows_html += f"<tr><td>{col}</td><td>{info['count']:,}</td><td>{pct}% {bar}</td><td><span class='pill {badge_class}'>{label}</span></td></tr>"
    return f"""<table><thead><tr><th>Column</th><th>Missing Count</th><th>Missing %</th><th>Status</th></tr></thead><tbody>{rows_html}</tbody></table>"""


def anomaly_html(anomalies: list) -> str:
    if not anomalies:
        return "<p style='color:var(--accent);margin-bottom:1.5rem'>✓ No anomalies detected (Z-score threshold: 3.0)</p>"
    html = "<h2>// Anomaly Flags</h2>"
    for a in anomalies:
        html += f"""<div class='anomaly-box'>
            <strong>⚠ {a['column']}</strong> — {a['count']:,} anomalous values ({a['pct']}% of rows)
            <br/><span style='color:var(--muted);font-size:0.78rem'>Detection method: {a['threshold']}</span>
        </div>"""
    return html


def numeric_html(numeric: dict) -> str:
    if not numeric:
        return "<p style='color:var(--muted)'>No numeric columns found.</p>"
    html = ""
    for col, s in numeric.items():
        html += f"""<div class='col-section'>
        <div class='col-name'>{col}</div>
        <div class='stat-row'>
            <div class='stat'><span class='stat-k'>Mean</span><span class='stat-v'>{s['mean']:,}</span></div>
            <div class='stat'><span class='stat-k'>Median</span><span class='stat-v'>{s['median']:,}</span></div>
            <div class='stat'><span class='stat-k'>Std Dev</span><span class='stat-v'>{s['std']:,}</span></div>
            <div class='stat'><span class='stat-k'>Min</span><span class='stat-v'>{s['min']:,}</span></div>
            <div class='stat'><span class='stat-k'>Max</span><span class='stat-v'>{s['max']:,}</span></div>
            <div class='stat'><span class='stat-k'>Q1 / Q3</span><span class='stat-v'>{s['q1']:,} / {s['q3']:,}</span></div>
            <div class='stat'><span class='stat-k'>Zeros</span><span class='stat-v'>{s['zeros']:,}</span></div>
            <div class='stat'><span class='stat-k'>Negatives</span><span class='stat-v'>{s['negatives']:,}</span></div>
        </div>
        </div>"""
    return html


def categorical_html(categorical: dict) -> str:
    if not categorical:
        return "<p style='color:var(--muted)'>No categorical columns found.</p>"
    html = ""
    for col, s in categorical.items():
        top_rows = ""
        total = sum(s["top_vals"].values())
        for val, cnt in s["top_vals"].items():
            pct = round(cnt / total * 100, 1) if total else 0
            top_rows += f"<tr><td>{val}</td><td>{cnt:,}</td><td>{pct}%</td></tr>"
        html += f"""<div class='col-section'>
        <div class='col-name'>{col} <span style='color:var(--muted);font-size:0.75rem;font-weight:300'>— {s['unique']} unique values</span></div>
        <table style='margin-bottom:0'><thead><tr><th>Value</th><th>Count</th><th>Share</th></tr></thead><tbody>{top_rows}</tbody></table>
        </div>"""
    return html


def df_to_html_table(df: pd.DataFrame, n: int = SAMPLE_ROWS) -> str:
    sample = df.head(n)
    headers = "".join(f"<th>{c}</th>" for c in sample.columns)
    rows_html = ""
    for _, row in sample.iterrows():
        cells = "".join(f"<td>{str(v)[:40]}</td>" for v in row)
        rows_html += f"<tr>{cells}</tr>"
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody></table>"


def generate_report(df: pd.DataFrame, results: dict, filename: str, output_path: str):
    anomaly_count = len(results["anomalies"])
    html = HTML_TEMPLATE.format(
        filename      = filename,
        timestamp     = datetime.now().strftime("%Y-%m-%d %H:%M"),
        rows          = f"{results['shape'][0]:,}",
        cols          = results['shape'][1],
        numeric_count = len(results["numeric"]),
        categorical_count = len(results["categorical"]),
        duplicates    = results["duplicates"],
        dup_class     = "danger" if results["duplicates"] > 0 else "",
        anomaly_count = anomaly_count,
        anom_class    = "warn" if anomaly_count > 0 else "",
        missing_table = missing_table_html(results["missing"]),
        anomaly_section = anomaly_html(results["anomalies"]),
        numeric_section = numeric_html(results["numeric"]),
        categorical_section = categorical_html(results["categorical"]),
        preview_table = df_to_html_table(df),
        sample_rows   = SAMPLE_ROWS,
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Report saved → {output_path}")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Automated CSV Report Generator")
    parser.add_argument("csv_path", help="Path to your CSV file")
    parser.add_argument("--output", "-o", default=None, help="Output HTML file path (optional)")
    args = parser.parse_args()

    if not os.path.isfile(args.csv_path):
        print(f"Error: file not found — '{args.csv_path}'")
        sys.exit(1)

    filename = os.path.basename(args.csv_path)
    output_path = args.output or filename.replace(".csv", "_report.html")

    print(f"\n🔍 Analyzing '{filename}' ...")
    df      = load_csv(args.csv_path)
    results = analyze(df)

    print(f"  {len(results['numeric'])} numeric cols · {len(results['categorical'])} categorical cols")
    print(f"  {results['duplicates']} duplicate rows · {len(results['anomalies'])} anomaly flags")

    generate_report(df, results, filename, output_path)
    print(f"\n✅ Done! Open '{output_path}' in your browser.\n")


if __name__ == "__main__":
    main()
