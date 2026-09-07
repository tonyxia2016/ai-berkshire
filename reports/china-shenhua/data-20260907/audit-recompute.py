"""Recheck the dated report sample against source values and Decimal formulas.

Observed facts, arithmetic, scenario assumptions and parser false positives are
classified separately. A numeric PASS does not imply independent second-source
coverage or validate a forecast. No network calls or report edits are performed.
"""

from decimal import Decimal, getcontext
from pathlib import Path
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPORT = HERE.parent / "中国神华研究报告-20260907.md"
getcontext().prec = 42
D = Decimal
source = json.loads((HERE / "audit-source-data.json").read_text())
quotes = json.loads((HERE / "quote-snapshots.json").read_text())
inputs = json.loads((HERE / "inputs.json").read_text())
u = source["sources"]
h = source["primary_h1"]
em = source["eastmoney"]
et = source["etnet"]

extraction = subprocess.run(
    [sys.executable, str(ROOT / "tools/report_audit.py"), "extract",
     "--report", str(REPORT.relative_to(ROOT)), "--seed", "42"],
    cwd=ROOT, check=True, text=True, capture_output=True).stdout
(HERE / "audit-extract.txt").write_text(extraction)
marker = "抽检清单 JSON（填入 fetched_value 后，传给 verdict 命令）："
sample = json.loads(extraction.split(marker, 1)[1].strip())
(HERE / "audit-sample.json").write_text(
    json.dumps(sample, ensure_ascii=False, indent=2) + "\n")

# Shares independently transcribed from the issued-shares page of the August
# return, cross-checked against the stored Tencent raw response.
shares, hshares = D("21689434304"), D("3377482000")
sina = re.search(r'="([^"]+)"', quotes["sina"]).group(1).split(",")
tencent = re.search(r'v_hk01088="([^"]+)"', quotes["tencent"]).group(1).split("~")
assert str(int(shares)) + ".00" in tencent
assert str(int(hshares)) + ".00" in tencent
p, pt = D(sina[6]), D(tencent[3])
a = D(re.search(r'="([^"]+)"', quotes["sina-A"]).group(1).split(",")[3])
fx = D("0.86465")
yi, million = D("100000000"), D("1000000")


def number(field):
    return D(str(h[field]))


def growth(now, prior):
    return (now / prior - 1) * 100


def solve_irr(cashflows):
    low, high = D("-0.99"), D("2")
    for _ in range(180):
        rate = (low + high) / 2
        npv = sum(cf / (1 + rate) ** year
                  for year, cf in enumerate(cashflows))
        if npv > 0:
            low = rate
        else:
            high = rate
    return (low + high) / 2 * 100


assumptions = inputs["valuation_assumptions"]
normal_eps = D(assumptions["normal_parent_profit_bn"]) * D("1000000000") / shares / fx
scenario_values = []
for scenario in assumptions["scenarios"]:
    g, pe, payout = (D(scenario[k]) for k in ("growth", "exit_pe", "payout"))
    eps = [normal_eps * (1 + g) ** year for year in (1, 2, 3)]
    dividends = [value * payout * D("0.8") for value in eps]
    exit_price = eps[-1] * pe
    after_tax = [-p, dividends[0], dividends[1], dividends[2] + exit_price]
    scenario_values.append({"price": exit_price, "tax_irr": solve_irr(after_tax)})

group_cash = number("cfo") - number("cash_capex") - number("cash_rou")
prior_group_cash = number("prior_cfo") - number("prior_cash_capex") - number("prior_cash_rou")
em_group_cash = D(em["cash_2026-06-30"]["NETCASH_OPERATE"]) - D(em["cash_2026-06-30"]["CONSTRUCT_LONG_ASSET"])
em_prior_cash = D(em["cash_2025-06-30"]["NETCASH_OPERATE"]) - D(em["cash_2025-06-30"]["CONSTRUCT_LONG_ASSET"])


def check(value, origin, value2=None, origin2="", kind="derived", note=""):
    return {"fetched_value": str(value), "fetched_source": origin,
            "fetched_value2": str(value2) if value2 is not None else None,
            "fetched_source2": origin2, "verification_kind": kind,
            "verification_note": note}


market_sources = "Decimal: Sina quote + HKEX shares + CFETS FX; " + u["sina_quote"]
market_sources2 = "Decimal: Tencent quote (earlier timestamp) + HKEX shares + CFETS FX; " + u["tencent_quote"]
primary = u["h1"]
values = {
    7: check(p * shares / yi, market_sources, pt * shares / yi, market_sources2),
    8: check(p * shares * fx / yi, market_sources, pt * shares * fx / yi, market_sources2),
    9: check((a * (shares-hshares) + p*hshares*fx) / yi, market_sources,
             (a * (shares-hshares) + pt*hshares*fx) / yi, market_sources2),
    23: check(number("cas_prior_profit") / 100, primary + " p.8 CAS reconciliation",
              D(em["main_2025-06-30"]["PARENTNETPROFIT"]) / yi, u["eastmoney_main"], "observed_dual_source"),
    24: check(growth(number("cas_profit"), number("cas_prior_profit")),
              "Decimal from IFRS-to-CAS reconciliation; " + primary,
              D(str(em["main_2026-06-30"]["PARENTNETPROFITTZ"])), u["eastmoney_main"]),
    27: check(growth(number("eps"), number("prior_eps")),
              "Decimal from IFRS note 12; " + primary,
              note="Restated EPS growth; not acquisition accretion."),
    29: check(number("prior_cfo") / 100, primary + " p.118",
              D(em["cash_2025-06-30"]["NETCASH_OPERATE"]) / yi, u["eastmoney_cash"], "observed_dual_source"),
    36: check(growth(group_cash, prior_group_cash), "Decimal from cash flow statement; " + primary,
              growth(em_group_cash, em_prior_cash), "Decimal from " + u["eastmoney_cash"]),
    51: check(number("rail_profit") / 100, primary + " segment note",
              et["h1_segment_profit"]["rail"], u["etnet_h1"], "observed_dual_source"),
    56: check(number("port_profit") / 100, primary + " segment note",
              et["h1_segment_profit"]["port"], u["etnet_h1"], "observed_dual_source"),
    57: check(D(source["primary_fy25"]["shipping_external_revenue"]) / 100,
              u["fy25"] + " segment note", et["fy25_external_revenue"]["shipping"],
              u["etnet_fy25"], "observed_dual_source"),
    58: check(number("shipping_external_revenue") / 100, primary + " segment note",
              et["h1_external_revenue"]["shipping"], u["etnet_h1"], "observed_dual_source"),
    60: check(number("shipping_margin_pct"), primary + " shipping segment operating analysis",
              kind="observed_primary_only", note="No independent second source. ETNet's 11.2% is revenue growth, not gross margin."),
    63: check(number("chemical_external_revenue") / 100, primary + " segment note",
              et["h1_external_revenue"]["chemical"], u["etnet_h1"], "observed_dual_source"),
    71: check(number("rail_km"), primary + " business overview",
              kind="observed_primary_only", note="Older broker reports corroborate the same mileage but do not independently verify current capacity."),
    72: check(number("port_million_tonnes_per_year") / 100, primary + " business overview",
              kind="observed_primary_only", note="Issuer describes approximately 270 million tonnes/year. No current independent engineering verification."),
    108: check(group_cash * million * 2 / (p * shares * fx) * 100,
               "Decimal: group cash flow / H-marked equity; " + primary,
               em_group_cash * 2 / (p * shares * fx) * 100, "Decimal from " + u["eastmoney_cash"],
               note="Consolidated CFO minus cash capex; not attributable FCFE."),
    109: check(D("0.98") * 2 / fx / p * 100,
               "Decimal, proposed dividend doubled; " + u["h1_dividend"],
               note="Mechanical annualization; not a committed full-year dividend."),
    115: check(D("45.74") * shares * D("0.86458") / (number("common_equity") * million),
               "Decimal: September 4 close / IFRS common BVPS; " + primary),
    130: check(scenario_values[0]["tax_irr"], "Independent Decimal cash-flow IRR; declared inputs.json assumptions",
               kind="scenario_arithmetic", note="Checks calculation only; EPS growth, payout, tax treatment and exit PE remain assumptions."),
    140: check(scenario_values[2]["price"], "Independent Decimal EPS compounding × exit PE; inputs.json",
               kind="scenario_arithmetic", note="Scenario, not an observed or promised market price."),
    144: check(scenario_values[2]["tax_irr"], "Independent Decimal cash-flow IRR; declared inputs.json assumptions",
               kind="scenario_arithmetic", note="Calculation check does not establish forecast probability."),
    152: check(D("38") / normal_eps, "Decimal: HK$38 band boundary / assumed normal EPS",
               kind="scenario_arithmetic", note="Parser selects the low endpoint 11.88x of the displayed 11.88–15.00x interval."),
    164: check(D(source["primary_fy25"]["revenue"]) / 100, u["fy25"] + " five-year summary",
               D(em["main_2025-12-31"]["OPERATE_INCOME_PK"]) / yi, u["eastmoney_main"], "observed_dual_source"),
}
noise = {163, 169}
assert {x["id"] for x in sample} == set(values) | noise, "Sample changed; review new points before issuing a verdict."
for item in sample:
    if item["id"] in noise:
        item.update(verification_kind="parser_false_positive",
                    verification_note="The extracted 2025 is a year/reference label, not a financial amount. Excluded transparently.")
    else:
        item.update(values[item["id"]])
        for key in ("fetched_value", "fetched_value2"):
            if item.get(key) is not None:
                deviation = abs(D(str(item["reported_value"])) - D(item[key])) / abs(D(str(item["reported_value"])))
                assert deviation <= D("0.01"), (item["id"], key, str(deviation))

results_text = json.dumps(sample, ensure_ascii=False, indent=2)
(HERE / "audit-results.json").write_text(results_text + "\n")
verdict = subprocess.run(
    [sys.executable, str(ROOT / "tools/report_audit.py"), "verdict",
     "--results", results_text, "--report", str(REPORT.relative_to(ROOT)), "--output-json"],
    cwd=ROOT, text=True, capture_output=True, check=True).stdout
(HERE / "audit-verdict.txt").write_text(re.sub(r"\x1b\[[0-9;]*m", "", verdict))
print(re.sub(r"\x1b\[[0-9;]*m", "", verdict))
counts = {}
for item in sample:
    kind = item["verification_kind"]
    counts[kind] = counts.get(kind, 0) + 1
print(json.dumps({"classification_counts": counts}, ensure_ascii=False))
