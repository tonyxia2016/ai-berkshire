"""Reproduce the dated research calculations with Decimal, without network calls.

The repository financial_rigor dedicated validators use Decimal. Its `calc`
command first evaluates native floats, so this research uses exact() and Decimal
for intermediate arithmetic and the dedicated validators for required checks.
All cash flows and scenario assumptions are explicitly named; group cash flow
must not be presented as cash attributable to the parent company's shareholders.
"""

from contextlib import redirect_stdout
from decimal import Decimal, getcontext
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))
import financial_rigor as rigor

getcontext().prec = 42
D = rigor.exact
data = json.loads((HERE / "inputs.json").read_text())
p, fx, shares, hs = map(D, [data[k] for k in
    ("price_hkd", "fx_cny_per_hkd", "shares", "h_shares")])
bn = D("1000000000")
h = {k: D(v) for k, v in data["h1"].items()}
assumptions = data["valuation_assumptions"]


def pct_change(now, prior):
    return (now / prior - 1) * 100


def dcf(cf, growth, discount, terminal=D("0"), years=10):
    explicit = sum(cf * (1 + growth) ** t / (1 + discount) ** t
                   for t in range(1, years + 1))
    continuation = cf * (1 + growth) ** years * (1 + terminal) / (discount - terminal)
    return explicit + continuation / (1 + discount) ** years


def implied_growth(cf, discount, terminal, years):
    low, high = D("-0.25"), D("0.5")
    for _ in range(160):
        mid = (low + high) / 2
        if dcf(cf, mid, discount, terminal=terminal, years=years) > p:
            high = mid
        else:
            low = mid
    return (low + high) / 2


def irr(price, dividends, terminal_price):
    low, high = D("-0.99"), D("2")
    for _ in range(160):
        mid = (low + high) / 2
        pv = sum(v / (1 + mid) ** t for t, v in enumerate(dividends, 1))
        pv += terminal_price / (1 + mid) ** len(dividends)
        if pv > price:
            low = mid
        else:
            high = mid
    return (low + high) / 2


metrics = {
    "h_marketcap_hkd_bn": p * hs / bn,
    "h_marked_total_marketcap_hkd_bn": p * shares / bn,
    "h_marked_total_marketcap_cny_bn": p * shares * fx / bn,
    "mixed_ah_marketcap_cny_bn": (D(data["a_price_cny"]) * (shares - hs) + p * hs * fx) / bn,
    "a_shares": shares - hs,
    "h_price_in_cny": p * fx,
    "h_discount_to_a_pct": (1 - p * fx / D(data["a_price_cny"])) * 100,
    "share_increase_pct": pct_change(shares, D(data["old_shares"])),
    "price_cross_source_difference_pct": abs(p-D(data["tencent_price_hkd"])) / p * 100,
    "h1_revenue_growth_pct": pct_change(h["revenue_bn"], h["prior_revenue_bn"]),
    "h1_ifrs_profit_growth_pct": pct_change(h["ifrs_parent_profit_bn"], h["prior_ifrs_parent_profit_bn"]),
    "h1_cas_profit_growth_pct": pct_change(h["cas_parent_profit_bn"], h["prior_cas_parent_profit_bn"]),
    "h1_reported_eps_growth_pct": pct_change(h["reported_eps_cny"], h["prior_reported_eps_cny"]),
    "h1_cfo_growth_pct": pct_change(h["cfo_bn"], h["prior_cfo_bn"]),
    "h1_gross_margin_pct": h["gross_profit_bn"] / h["revenue_bn"] * 100,
    "h1_prior_gross_margin_pct": h["prior_gross_profit_bn"] / h["prior_revenue_bn"] * 100,
    "h1_operating_margin_proxy_pct": (h["gross_profit_bn"] - h["selling_bn"] - h["admin_bn"] - h["rd_expensed_bn"]) / h["revenue_bn"] * 100,
    "liquid_assets_bn": h["cash_bn"] + h["time_deposits_bn"] + h["structured_deposits_bn"],
    "cas_cash_reconciliation_bn": h["cash_bn"] + h["time_deposits_bn"] + h["restricted_deposits_bn"],
    "cash_capex_including_land_bn": h["cash_capex_bn"] + h["land_rights_cash_bn"],
    "annualized_ifrs_parent_eps_hkd": h["ifrs_parent_profit_bn"] * 2 * bn / shares / fx,
    "annualized_cas_parent_eps_hkd": h["cas_parent_profit_bn"] * 2 * bn / shares / fx,
    "parent_bvps_hkd": h["parent_equity_bn"] * bn / shares / fx,
    "annualized_revenue_per_share_hkd": h["revenue_bn"] * 2 * bn / shares / fx,
    "annualized_h1_dps_hkd": h["proposed_dps_cny"] * 2 / fx,
    "proposed_h1_dividend_total_bn": h["proposed_dps_cny"] * shares / bn,
    "h1_single_dividend_yield_pct": h["proposed_dps_cny"] / fx / p * 100,
    "trailing_declared_fy25_dividend_yield_pct": D("2.01") / fx / p * 100,
    "annualized_h1_dividend_yield_pct": h["proposed_dps_cny"] * 2 / fx / p * 100,
    "annualized_h1_dividend_yield_after_20pct_tax_pct": h["proposed_dps_cny"] * 2 / fx / p * 80,
    "debt_to_assets_pct": h["total_liabilities_bn"] / h["total_assets_bn"] * 100,
    "project_capex_plan_completion_pct": h["project_capex_bn"] / h["annual_project_capex_plan_bn"] * 100,
}
metrics["narrow_net_debt_bn"] = (h["current_borrowings_bn"] + h["noncurrent_borrowings_bn"]
    + h["separately_presented_lease_liabilities_bn"] - metrics["liquid_assets_bn"])
metrics["group_cfo_less_cash_capex_bn"] = h["cfo_bn"] - metrics["cash_capex_including_land_bn"]
metrics["group_cash_stress_before_investment_income_bn"] = (metrics["group_cfo_less_cash_capex_bn"]
    - h["cash_interest_paid_bn"] - h["cash_lease_principal_bn"]
    - h["cash_lease_interest_bn"] - h["cash_nci_dividend_bn"])
metrics["group_cash_stress_after_investment_income_bn"] = (
    metrics["group_cash_stress_before_investment_income_bn"]
    + h["cash_associate_dividend_bn"] + h["cash_interest_received_bn"])
metrics["group_cash_stress_coverage_low"] = metrics["group_cash_stress_before_investment_income_bn"] / metrics["proposed_h1_dividend_total_bn"]
metrics["group_cash_stress_coverage_high"] = metrics["group_cash_stress_after_investment_income_bn"] / metrics["proposed_h1_dividend_total_bn"]
metrics["h1_payout_ifrs_pct"] = metrics["proposed_h1_dividend_total_bn"] / h["ifrs_parent_profit_bn"] * 100
metrics["h1_payout_cas_pct"] = metrics["proposed_h1_dividend_total_bn"] / h["cas_parent_profit_bn"] * 100
metrics["pe_h1_annualized_ifrs"] = p / metrics["annualized_ifrs_parent_eps_hkd"]
metrics["pe_h1_annualized_cas"] = p / metrics["annualized_cas_parent_eps_hkd"]
metrics["pb"] = p / metrics["parent_bvps_hkd"]
metrics["ps_h1_annualized"] = p / metrics["annualized_revenue_per_share_hkd"]
metrics["roe_h1_annualized_on_closing_equity_pct"] = h["ifrs_parent_profit_bn"] * 2 / h["parent_equity_bn"] * 100
metrics["group_fcf_to_h_marked_equity_annualized_pct"] = metrics["group_cfo_less_cash_capex_bn"] * 2 / metrics["h_marked_total_marketcap_cny_bn"] * 100
metrics["ev_proxy_cny_bn"] = metrics["h_marked_total_marketcap_cny_bn"] + metrics["narrow_net_debt_bn"] + h["nci_equity_bn"]
metrics["ev_proxy_to_annualized_sales"] = metrics["ev_proxy_cny_bn"] / (h["revenue_bn"] * 2)

normal_eps = D(assumptions["normal_parent_profit_bn"]) * bn / shares / fx
metrics["normal_eps_hkd"] = normal_eps
metrics["normal_pe"] = p / normal_eps
metrics["normal_value_at_10pe"] = normal_eps * 10
metrics["normal_value_at_12pe"] = normal_eps * 12

dcf_results = []
dcf_years = int(assumptions["dcf_years"])
terminal_growth = D(assumptions["dcf_terminal_growth"])
for cash_bn in assumptions["owner_cashflow_bn"]:
    cf = D(cash_bn) * bn / shares / fx
    for discount in assumptions["discount_rates"]:
        r = D(discount)
        dcf_results.append({
            "normal_owner_cashflow_cny_bn": cash_bn,
            "discount_rate": r,
            "normal_cashflow_per_share_hkd": cf,
            "normal_cashflow_yield_pct": cf / p * 100,
            "explicit_years": dcf_years,
            "terminal_growth": terminal_growth,
            "value_hkd": dcf(cf, D(assumptions["dcf_first_stage_growth"]), r,
                             terminal=terminal_growth, years=dcf_years),
            "implied_first_stage_growth_pct_at_current_price": implied_growth(
                cf, r, terminal_growth, dcf_years) * 100,
        })

scenarios = []
for scenario in assumptions["scenarios"]:
    growth, exit_pe, payout = map(D, [scenario[k] for k in ("growth", "exit_pe", "payout")])
    eps3 = normal_eps * (1 + growth) ** 3
    dividends = [normal_eps * (1 + growth) ** year * payout for year in (1, 2, 3)]
    terminal_price = eps3 * exit_pe
    scenarios.append({
        **scenario,
        "year3_eps_hkd": eps3,
        "year3_price_hkd": terminal_price,
        "dividends_hkd": dividends,
        "cumulative_dividend_hkd": sum(dividends),
        "total_return_pct": ((terminal_price + sum(dividends)) / p - 1) * 100,
        "annual_irr_pct": irr(p, dividends, terminal_price) * 100,
        "annual_irr_after_20pct_dividend_tax_pct": irr(p, [v * D("0.8") for v in dividends], terminal_price) * 100,
        "entry_price_for_10pct_irr_hkd": sum(v / D("1.1") ** t for t, v in enumerate(dividends, 1)) + terminal_price / D("1.1") ** 3,
    })

bands = []
for price in ("30", "33", "38", "44.72", "48"):
    price_d = D(price)
    base = scenarios[1]
    bands.append({"price_hkd": price_d,
        "pe_at_normal_profit": price_d / normal_eps,
        "annualized_h1_dividend_yield_pct": metrics["annualized_h1_dps_hkd"] / price_d * 100,
        "base_annual_irr_pct": irr(price_d, base["dividends_hkd"], base["year3_price_hkd"]) * 100})

result = {"metrics": metrics, "dcf": dcf_results, "scenarios": scenarios, "price_bands": bands}
(HERE / "calculations.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n")

with (HERE / "verification.txt").open("w") as log, redirect_stdout(log):
    print("Price and financial statement cutoffs are documented in inputs.json.")
    print("Validator label 'TTM' below is generic; EPS/revenue here are H1 × 2, not TTM.")
    rigor.verify_market_cap(data["tencent_price_hkd"], data["shares"], data["tencent_total_marketcap_hkd"], "HKD, Tencent 14:57:20")
    rigor.verify_market_cap(data["tencent_price_hkd"], data["h_shares"], data["tencent_h_marketcap_hkd"], "HKD, H class Tencent")
    rigor.verify_market_cap(p, shares, "969951502075", "HKD, report H-marked total equity")
    rigor.verify_market_cap(p, hs, "151040995040", "HKD, report H class")
    rigor.cross_validate("H-share snapshots, different timestamps", {"Sina 15:12:25": p, "Tencent 14:57:20": data["tencent_price_hkd"]}, "HKD", tolerance_pct=1)
    rigor.cross_validate("Issued shares", {"HKEX August return issued page": data["shares"], "Tencent quote": data["shares"]}, "shares", tolerance_pct=1)
    rigor.cross_validate("2026H1 revenue", {"HKEX IFRS": "189.338", "AAStocks earnings summary": "189.338", "Eastmoney data": "189.338"}, "CNY bn", tolerance_pct=1)
    rigor.cross_validate("2026H1 IFRS parent profit", {"HKEX IFRS": "31.054", "AAStocks earnings summary": "31.054"}, "CNY bn", tolerance_pct=1)
    rigor.cross_validate("2026H1 CFO", {"HKEX IFRS": "54.664", "Eastmoney cash flow": "54.664"}, "CNY bn", tolerance_pct=1)
    rigor.cross_validate("2026H1 CAS monetary funds", {"HKEX CAS": "135.592", "Eastmoney balance sheet": "135.592"}, "CNY bn", tolerance_pct=1)
    rigor.verify_valuation(p, eps=metrics["annualized_ifrs_parent_eps_hkd"], bvps=metrics["parent_bvps_hkd"], dividend=metrics["annualized_h1_dps_hkd"], revenue_per_share=metrics["annualized_revenue_per_share_hkd"])
    print("The following FCF is consolidated CFO minus cash capex; NOT attributable FCFE.")
    rigor.verify_valuation(p, fcf_per_share=metrics["group_cfo_less_cash_capex_bn"] * 2 * bn / shares / fx)
    rigor.three_scenario_valuation(p, normal_eps, shares / D("100000000"),
        *[D(s["growth"]) for s in assumptions["scenarios"]],
        *[D(s["exit_pe"]) for s in assumptions["scenarios"]], years=3, currency="HKD")
    print("Additional exact Decimal calculations, distributions, IRR and reverse DCF:")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

print(json.dumps({"metrics": metrics, "scenarios": scenarios, "dcf": dcf_results}, ensure_ascii=False, indent=2, default=str))
