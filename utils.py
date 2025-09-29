from jinja2 import Template
from datetime import datetime, timezone

def format_cell(value):
    """
    خروجی هر اندیکاتور رو به صورت (متن، کلاس) برمی‌گردونه.
    """
    if value == "ND" or value is None:
        return ("ND", "nd")
    if value is True or str(value).strip() in ["✅", "True"]:
        return ("✅", "green")
    if value is False or str(value).strip() in ["❌", "False"]:
        return ("❌", "red")
    return (str(value), "nd")  # هر مقدار ناشناخته را هم برمی‌گردونه

def save_html(results, tfs, file_name="scan.html"):
    """
    ذخیره HTML کنار main.py با نمایش تمام تایم‌فریم‌ها
    فقط ستون‌های تایم‌فریم‌هایی که داده دارند، نمایش داده می‌شوند
    """
    # تعداد ستون‌ها برای هر تایم‌فریم
    COLUMNS_PER_TF = 23

    template = Template("""
<html>
<head><meta charset="utf-8"><title>CoinEx Scan</title>
<style>
body{font-family:Arial;background:#f4f4f4;}
table{border-collapse:collapse;width:100%;min-width:1800px;}
th, td{border:1px solid #ddd; padding:6px; text-align:center; font-size:12px;}
th{background:#222;color:#fff;}
.fixed-header {position: sticky;top:0;z-index:10;width: 100%;}
.symbol-name{font-weight:bold;color:aquamarine;background:#222;}
.nd{color:#999; font-style:italic;}
.green{color:limegreen;font-weight:bold;}
.red{color:crimson;font-weight:bold;}
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
<th colspan="{{ columns }}">{{ tf }}</th>
{% endfor %}
</tr>
<tr>
{% for tf in tfs %}
<th>CM55</th><th>M55</th><th>M200</th><th>CM200</th>
<th>DM</th><th>DR</th><th>MR</th><th>SROS</th><th>SROB</th><th>SRD</th>
<th>CCI14 OB</th><th>CCI14 OS</th><th>CCI14 S</th><th>CCI14 N</th><th>CCI14 M</th>
<th>CCI50 OB</th><th>CCI50 OS</th><th>CCI50 S</th><th>CCI50 N</th><th>CCI50 M</th>
<th>OBV DN</th><th>OBV DS</th><th class="tf-border-right">OBV M</th>
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
<td class="{{ c.get('cm55_fmt', ('ND','nd'))[1] }}">{{ c.get('cm55_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('m55_fmt', ('ND','nd'))[1] }}">{{ c.get('m55_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('m200_fmt', ('ND','nd'))[1] }}">{{ c.get('m200_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cm200_fmt', ('ND','nd'))[1] }}">{{ c.get('cm200_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('dm_fmt', ('ND','nd'))[1] }}">{{ c.get('dm_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('dr_fmt', ('ND','nd'))[1] }}">{{ c.get('dr_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('mr_fmt', ('ND','nd'))[1] }}">{{ c.get('mr_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('sros_fmt', ('ND','nd'))[1] }}">{{ c.get('sros_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('srob_fmt', ('ND','nd'))[1] }}">{{ c.get('srob_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('srd_fmt', ('ND','nd'))[1] }}">{{ c.get('srd_fmt', ('ND','nd'))[0] }}</td>

<td class="{{ c.get('cci14_ob_fmt', ('ND','nd'))[1] }}">{{ c.get('cci14_ob_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cci14_os_fmt', ('ND','nd'))[1] }}">{{ c.get('cci14_os_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cci14_s_fmt', ('ND','nd'))[1] }}">{{ c.get('cci14_s_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cci14_n_fmt', ('ND','nd'))[1] }}">{{ c.get('cci14_n_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cci14_m_fmt', ('ND','nd'))[1] }}">{{ c.get('cci14_m_fmt', ('ND','nd'))[0] }}</td>

<td class="{{ c.get('cci50_ob_fmt', ('ND','nd'))[1] }}">{{ c.get('cci50_ob_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cci50_os_fmt', ('ND','nd'))[1] }}">{{ c.get('cci50_os_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cci50_s_fmt', ('ND','nd'))[1] }}">{{ c.get('cci50_s_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cci50_n_fmt', ('ND','nd'))[1] }}">{{ c.get('cci50_n_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('cci50_m_fmt', ('ND','nd'))[1] }}">{{ c.get('cci50_m_fmt', ('ND','nd'))[0] }}</td>

<td class="{{ c.get('obv_dn_fmt', ('ND','nd'))[1] }}">{{ c.get('obv_dn_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('obv_ds_fmt', ('ND','nd'))[1] }}">{{ c.get('obv_ds_fmt', ('ND','nd'))[0] }}</td>
<td class="{{ c.get('obv_m_fmt', ('ND','nd'))[1] }} tf-border-right">{{ c.get('obv_m_fmt', ('ND','nd'))[0] }}</td>
{% else %}
{% for i in range(columns) %}
<td class="nd{% if i==columns-1 %} tf-border-right{% endif %}">ND</td>
{% endfor %}
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
        tfs=tfs,
        columns=COLUMNS_PER_TF
    )
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html)
