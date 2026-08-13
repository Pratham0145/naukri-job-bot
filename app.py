'''
Naukri Auto Job Applier
app.py — Web dashboard to view applied jobs history

Usage:
    python app.py
    Then open http://localhost:5000
'''

import csv
import os
from flask import Flask, render_template_string
from config.settings import applied_jobs_csv, failed_jobs_csv

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Naukri Bot — Applied Jobs</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #f5f5f5; color: #222; }
  header { background: #4a90d9; color: #fff; padding: 18px 32px; }
  header h1 { font-size: 22px; font-weight: 600; }
  header p  { font-size: 13px; opacity: .8; margin-top: 4px; }
  .stats { display: flex; gap: 16px; padding: 20px 32px; flex-wrap: wrap; }
  .stat-card { background: #fff; border-radius: 10px; padding: 16px 24px;
               box-shadow: 0 1px 4px rgba(0,0,0,.08); min-width: 140px; }
  .stat-card .num { font-size: 32px; font-weight: 700; color: #4a90d9; }
  .stat-card .lbl { font-size: 13px; color: #666; margin-top: 4px; }
  .section { padding: 0 32px 32px; }
  .section h2 { font-size: 17px; font-weight: 600; margin-bottom: 12px;
                padding-top: 8px; border-top: 1px solid #e0e0e0; }
  table { width: 100%; border-collapse: collapse; background: #fff;
          border-radius: 10px; overflow: hidden;
          box-shadow: 0 1px 4px rgba(0,0,0,.08); font-size: 14px; }
  th { background: #f0f4fa; padding: 10px 14px; text-align: left;
       font-weight: 600; font-size: 13px; color: #555; }
  td { padding: 10px 14px; border-top: 1px solid #f0f0f0; }
  tr:hover td { background: #f9fbff; }
  a { color: #4a90d9; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 10px;
           font-size: 11px; font-weight: 600; }
  .badge-ok  { background: #e6f4ea; color: #2d7a4f; }
  .badge-err { background: #fdecea; color: #c0392b; }
  .empty { padding: 24px; text-align: center; color: #999; font-size: 14px; }
</style>
</head>
<body>
<header>
  <h1>Naukri Auto Job Applier — Dashboard</h1>
  <p>Applied jobs history | Refresh page to update</p>
</header>

<div class="stats">
  <div class="stat-card"><div class="num">{{ applied|length }}</div><div class="lbl">Applied</div></div>
  <div class="stat-card"><div class="num">{{ failed|length }}</div><div class="lbl">Failed</div></div>
  <div class="stat-card"><div class="num">{{ (applied|length) + (failed|length) }}</div><div class="lbl">Total Processed</div></div>
</div>

<div class="section">
  <h2>✅ Applied Jobs</h2>
  {% if applied %}
  <table>
    <tr><th>#</th><th>Job Title</th><th>Company</th><th>Location</th><th>Applied At</th><th>Link</th></tr>
    {% for row in applied %}
    <tr>
      <td>{{ loop.index }}</td>
      <td>{{ row.job_title }}</td>
      <td>{{ row.company }}</td>
      <td>{{ row.location }}</td>
      <td>{{ row.timestamp }}</td>
      <td>{% if row.url %}<a href="{{ row.url }}" target="_blank">View</a>{% endif %}</td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <div class="empty">No applications recorded yet. Run the bot first.</div>
  {% endif %}
</div>

<div class="section">
  <h2>❌ Failed Applications</h2>
  {% if failed %}
  <table>
    <tr><th>#</th><th>Job Title</th><th>Company</th><th>Reason</th><th>Time</th></tr>
    {% for row in failed %}
    <tr>
      <td>{{ loop.index }}</td>
      <td>{{ row.job_title }}</td>
      <td>{{ row.company }}</td>
      <td><span class="badge badge-err">{{ row.reason }}</span></td>
      <td>{{ row.timestamp }}</td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <div class="empty">No failed applications.</div>
  {% endif %}
</div>
</body>
</html>
"""


def read_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@app.route("/")
def index():
    applied = list(reversed(read_csv(applied_jobs_csv)))
    failed  = list(reversed(read_csv(failed_jobs_csv)))
    return render_template_string(HTML, applied=applied, failed=failed)


if __name__ == "__main__":
    print("Dashboard running at http://localhost:5000")
    app.run(debug=False, port=5000)
