# utils.py

from jinja2 import Template
from datetime import datetime, timezone

def format_cell(value):
    """
    قالب‌بندی مقدار برای نمایش در جدول HTML.
    اگر مقدار "ND" باشد، نشان می‌دهد Not Determined.
    اگر مقدار True یا "✅" باشد به رنگ سبز.
    اگر مقدار False یا "❌" باشد به رنگ قرمز.
    """
    if value == "ND":
        return ("ND", "nd")
    if value is True or value == "✅":
        return ("✅", "green")
    if value is False or value == "❌":
        return ("❌", "red")
    # اگر عدد یا رشته‌ای دیگر باشد، نمایش عادی
    return (str(value), "nd")

def save_html(results, REQUEST_TFS, file_name="output.html"):
    """
    رندر کردن نتایج به قالب HTML با استفاده از Jinja2.
    results باید به شکل:
      { symbol: { tf: { key1: val1, key2: val2, … }, … }, … }
    REQUEST_TFS لیستی از تایم‌فریم‌ها است (مثلاً ["12h", "1d", …]).
    """
    template = Template("""
    <html>
    <head>
       <meta charset="utf-8">
title>Scanner Results</title>
       <style>
         .green { background-color: #c8f7c5; }
         .red { background-color: #f7c5c5; }
         .nd { background-color: #f0f0f0; }
         table, th, td { border: 1px solid black; border-collapse: collapse; padding: 4px; }
       </style>
    </head>
    <body>
      <h2>CoinEx Scanner ({{ now }})</h2>
      <table>
        <thead>
          <tr>
            <th>نماد</th>
            <th>تایم‌فریم</th>
            <th>MA55</th><th>Cross MA55</th>
            <th>MA200</th><th>Cross MA200</th>
            <th>DM</th><th>DR</th><th>MR</th>
            <th>StochK</th><th>StochD</th>
            <th>OBV</th><th>CCI14</th><th>CCI50</th>
          </tr>
        </thead>
        <tbody>
        {% for symbol, tfs_data in results.items() %}
          {% for tf in tfs %}
            {% set cell = tfs_data.get(tf) %}
            {% if cell %}
            <tr>
              <td>{{ symbol }}</td>
              <td>{{ tf }}</td>
              {% for key in ["m55_fmt", "cm55_fmt", "m200_fmt", "cm200_fmt", "dm_fmt", "dr_fmt", "mr_fmt"] %}
                {% set v, cls = format_cell(cell.get(key)) %}
                <td class="{{ cls }}">{{ v }}</td>
              {% endfor %}
              {# برای اندیکاتورهای جدید #}
              {% set v, cls = format_cell(cell.get("stoch_k_fmt")) %}
              <td class="{{ cls }}">{{ v }}</td>
              {% set v, cls = format_cell(cell.get("stoch_d_fmt")) %}
              <td class="{{ cls }}">{{ v }}</td>
              {% set v, cls = format_cell(cell.get("obv_fmt")) %}
              <td class="{{ cls }}">{{ v }}</td>
              {% set v, cls = format_cell(cell.get("cci14_fmt")) %}
              <td class="{{ cls }}">{{ v }}</td>
              {% set v, cls = format_cell(cell.get("cci50_fmt")) %}
              <td class="{{ cls }}">{{ v }}</td>
            </tr>
            {% endif %}
          {% endfor %}
        {% endfor %}
        </tbody>
      </table>
    </body>
    </html>
    """)
    html = template.render(
        now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        results=results,
        tfs=REQUEST_TFS,
        format_cell=format_cell
    )
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html)
