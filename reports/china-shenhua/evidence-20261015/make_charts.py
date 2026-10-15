"""Create two small vector charts from the independently collected source data."""
import json
from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "financials-verified.json").read_text())
FONT = "'PingFang SC','Hiragino Sans GB',Arial,sans-serif"


def text(x, y, value, size=16, fill="#334155", anchor="start", weight="400"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{escape(str(value))}</text>')


def start(width, height, title, subtitle):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
            text(40, 44, title, 24, "#0f172a", weight="600"),
            text(40, 75, subtitle, 14, "#64748b")]


names = ["煤炭", "发电", "铁路", "港口", "航运", "煤化工"]
colors = ["#334155", "#2c7a7b", "#55839a", "#7390a2", "#97acb9", "#ad825b"]
parts = start(920, 460, "收入主要来自煤，物流的价值在利润和交付", "2026H1 外部收入结构｜合并抵销后｜金额：人民币亿元")
total = Decimal(data["h1"]["revenue"])
for i, row in enumerate(data["segments_h1"]):
    value = Decimal(row["external_revenue"]) / Decimal(100)
    share = Decimal(row["external_revenue"]) / total * 100
    y = 117 + i * 43
    width = float(share) / 65 * 575
    parts.extend([text(40, y + 19, names[i]),
        f'<rect x="130" y="{y}" width="{width:.2f}" height="26" rx="3" fill="{colors[i]}"/>',
        text(145 + width, y + 19, f"{share:.2f}%  ·  {value:,.2f}", 15)])
parts.append(text(40, 412, "铁路与港口的内部分部收入已抵销；不能按外部收入占比判断其全部价值。", 14, "#64748b"))
parts.append(text(40, 439, "来源：中国神华 2026 年中报，分部附注。", 12, "#64748b"))
parts.append("</svg>")
(HERE / "revenue-mix.svg").write_text("\n".join(parts))

parts = start(920, 510, "五年盈利与现金投入", "2021—2025 财务轮廓｜金额：人民币亿元｜并购前各年度历史口径")
series = [("归母利润（IFRS）", "ifrs_parent_profit", "#334155"),
          ("经营现金流", "cfo", "#2c7a7b"),
          ("现金资产投入", "cash_capex_incl_rou_cash", "#ad825b")]
left, top, width, height = 82, 124, 760, 265
for tick in (0, 300, 600, 900, 1200):
    y = top + height - tick / 1200 * height
    parts.append(f'<rect x="{left}" y="{y}" width="{width}" height="1" fill="#e2e8f0"/>')
    parts.append(text(left - 16, y + 5, tick, 13, "#64748b", "end"))
for i, row in enumerate(data["annual"]):
    parts.append(text(left + 76 + i * width / 5, 416, row["year"], 14, "#334155", "middle"))
for j, (label, key, color) in enumerate(series):
    for i, row in enumerate(data["annual"]):
        val = Decimal(str(row[key])) / Decimal(100)
        x = left + 21 + i * width / 5 + j * 36
        bar_height = float(val) / 1200 * height
        y = top + height - bar_height
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="30" height="{bar_height:.2f}" rx="2" fill="{color}"/>')
        parts.append(text(x + 15, y - 10, f"{val:.1f}", 11, color, "middle"))
for i, (label, _, color) in enumerate(series):
    x = 82 + i * 270
    parts.append(f'<rect x="{x}" y="442" width="24" height="16" rx="2" fill="{color}"/>')
    parts.append(text(x + 37, 458, label, 14))
parts.append(text(40, 493, "来源：公司年报。损益为五年摘要，现金流为各年原报；未统一回溯所有历史收购，亦非归母 FCFE。", 12, "#64748b"))
parts.append("</svg>")
(HERE / "financial-trend.svg").write_text("\n".join(parts))
print("Created revenue-mix.svg and financial-trend.svg")
