from jinja2 import Template
from datetime import datetime, timezone

def format_cell(value):
    if value == "ND":
        return ("ND","nd")
    if value is True or value=="✅":
        return ("✅","green")
    if value is False or value=="❌":
        return ("❌","red")
    return ("ND","nd")

def save_html(results, REQUEST_TFS, file_name="output.html"):
    template = Template("""
<html>
<head><meta charset="utf-8"><title>CoinEx Scan</title>
<style>
body{font-family:Arial;background:#f4f4f4;}
table{border-collapse:collapse;width:100%;min-width:1200px;}
th, td{border:1px solid #ddd; padding:6px; text-align:center; font-size:12px;}
th{background:#222;color:#fff;}
.fixed-header {position: sticky;top:0;z-index:10;width: 100%;}
.symbol-name{font-weight:bold;color:aquamarine;background:#222;}
.nd{color:#999; font-style:italic;}
.green, .red{font-size:12px; font-weight:bold;}
.tf-border-right{border-right:3px solid #222;}
tbody tr{border-bottom:2px solid #000;}
tbody tr:hover{background-color:#333;color:#fff;}
</style>
</head>
<body>
<h2>CoinEx Scanner ({{ now }})</h2>
<table>
<thead class="fixed-header">
<tr>
<th rowspan="2">#</th>
<th rowspan="2">نماد</th>
{% for tf in tfs %}
<th colspan="7">{{ tf }}</th>
{% endfor %}
</tr>
<tr>
{% for tf in tfs %}
<th>CM55</th><th>M55</th><th>M200</th><th>CM200</th><th>DM</th><th>DR</th><th class="tf-border-right">MR</th>
{% endfor %}
</tr>
</thead>
<tbody>
{% for s,data in results.items() %}
<tr>
<td>{{ loop.index }}</td><td class="symbol-name">{{ s }}</td>
{% for tf in tfs %}
{% set c = data.get(tf) %}
{% if c %}
<td class="{{ c.cm55_fmt[1] }}">{{ c.cm55_fmt[0] }}</td>
<td class="{{ c.m55_fmt[1] }}">{{ c.m55_fmt[0] }}</td>
<td class="{{ c.m200_fmt[1] }}">{{ c.m200_fmt[0] }}</td>
<td class="{{ c.cm200_fmt[1] }}">{{ c.cm200_fmt[0] }}</td>
<td class="{{ c.dm_fmt[1] }}">{{ c.dm_fmt[0] }}</td>
<td class="{{ c.dr_fmt[1] }}">{{ c.dr_fmt[0] }}</td>
<td class="{{ c.mr_fmt[1] }} tf-border-right">{{ c.mr_fmt[0] }}</td>
{% else %}
<td class="nd">ND</td><td class="nd">ND</td><td class="nd">ND</td><td class="nd">ND</td><td class="nd">ND</td><td class="nd">ND</td><td class="nd tf-border-right">ND</td>
{% endif %}
{% endfor %}
</tr>
{% endfor %}
</tbody>
</table>
</body>
</html>
""")
    html = template.render(
        now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        results=results,
        tfs=REQUEST_TFS
    )
    with open(file_name,"w",encoding="utf-8") as f:
        f.write(html)
