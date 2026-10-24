"""Reproducible financial evidence checks; figures are RMB million unless noted."""
from pathlib import Path
from decimal import Decimal
import json
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
RIGOR = ROOT / "tools/financial_rigor.py"
checks = []
log = []

def run(*args):
    r = subprocess.run(["python3", str(RIGOR), *args], text=True, capture_output=True, check=True)
    log.append(r.stdout)

def cross(field, primary, secondary, secondary_name="Eastmoney", unit="RMB million"):
    values = {"Original filing": primary, secondary_name: secondary}
    run("cross-validate", "--field", field, "--values", json.dumps(values), "--unit", unit)
    diff = abs(Decimal(str(primary)) - Decimal(str(secondary))) / abs(Decimal(str(primary))) * 100 if primary else Decimal(0)
    checks.append({"field": field, "primary": primary, "secondary": secondary, "error_pct": str(diff), "unit": unit})

def latest(stem):
    return json.loads((BASE / (stem + ".json")).read_text())["result"]["data"][0]

main = latest("financials-eastmoney-main")
income = latest("financials-eastmoney-income")
bs = latest("financials-eastmoney-balance")
cf = latest("financials-eastmoney-cashflow")
hkmain = latest("financials-RPT_HKF10_FN_MAININDICATOR")
hkbs = {r["ITEM_NAME"]: r["AMOUNT"] for r in json.loads((BASE / "financials-RPT_HKF10_FN_BALANCE.json").read_text())["result"]["data"]}

current = {
    "revenue": 296031, "revenue_prior_restated": 271651,
    "cas_parent_profit": 44403, "cas_parent_profit_prior_restated": 42780,
    "cas_deducted_parent_profit": 42808, "cas_deducted_parent_profit_prior": 38704,
    "cas_eps": 2.062, "cas_eps_prior_restated": 2.019,
    "ifrs_parent_profit": 47317, "ifrs_parent_profit_prior_restated": 46336,
    "ifrs_eps": 2.198, "ifrs_eps_prior_restated": 2.187,
    "cas_cost_of_sales": 192458, "cas_operating_profit": 70397,
    "ifrs_cost_of_sales": 209285, "ifrs_gross_profit": 86746,
    "ifrs_profit_before_tax": 72721, "ifrs_group_net_profit": 57675,
    "cas_profit_before_tax": 69609, "cas_group_net_profit": 54555,
    "cfo": 92700, "cfo_prior_restated": 75315,
    "cash_capex": 47181, "cash_capex_ppe": 44969, "cash_capex_rou": 2212,
    "cash_capex_prior_restated": 40047,
    "cash_equivalents": 59755, "deposits_over_3m": 57947, "restricted_cash": 15472,
    "cas_monetary_funds": 133174, "current_fvtpl": 0,
    "current_borrowings": 79462, "noncurrent_borrowings": 76040,
    "current_lease_liabilities": 181, "noncurrent_lease_liabilities": 1087,
    "narrow_net_debt": 39068,
    "cas_parent_equity": 444569, "ifrs_parent_equity": 453033,
    "cas_total_assets": 915140, "ifrs_total_assets": 924371,
    "total_liabilities": 373646, "cas_dividends_payable": 23367,
    "borrowings_interest_paid": 3929, "lease_interest_paid": 19, "lease_principal_paid": 566,
    "nci_dividends_paid": 6169, "parent_dividends_paid": 22342,
    "common_control_acquisition_cash": 90942, "associate_investment_cash": 9353,
    "associate_dividends_received": 2456, "interest_received": 1141,
    "factoring_repayment": 6097, "factoring_and_bill_discount_proceeds": 7287,
    "total_shares": 21689434304, "h_shares": 3377482000, "a_shares": 18311952304,
}

for field, value, row, key in [
    ("9M revenue CAS",296031,income,"OPERATE_INCOME"),
    ("9M parent profit CAS",44403,income,"PARENT_NETPROFIT"),
    ("9M operating profit CAS",70397,income,"OPERATE_PROFIT"),
    ("9M cost of sales CAS",192458,income,"OPERATE_COST"),
    ("9M deducted parent profit CAS",42808,income,"DEDUCT_PARENT_NETPROFIT"),
    ("9M CFO",92700,cf,"NETCASH_OPERATE"),
    ("9M cash capex",47181,cf,"CONSTRUCT_LONG_ASSET"),
    ("September cash equivalents",59755,cf,"END_CCE"),
    ("September monetary funds CAS",133174,bs,"MONETARYFUNDS"),
    ("September dividends payable",23367,bs,"DIVIDEND_PAYABLE"),
    ("September parent equity CAS",444569,bs,"TOTAL_PARENT_EQUITY"),
    ("September total liabilities",373646,bs,"TOTAL_LIABILITIES"),
    ("9M NCI cash dividends",6169,cf,"SUBSIDIARY_PAY_DIVIDEND"),
    ("9M IFRS profit",47317,hkmain,"HOLDER_PROFIT"),
    ("9M IFRS gross profit",86746,hkmain,"GROSS_PROFIT"),
    ("September IFRS equity",453033,hkmain,"TOTAL_PARENT_EQUITY"),
]: cross(field,value,row[key]/1000000)
cross("9M CAS EPS",2.062,income["BASIC_EPS"],unit="RMB/share")
cross("9M IFRS EPS",2.198,hkmain["BASIC_EPS"],unit="RMB/share")
cross("Total shares",21689434304,hkmain["ISSUED_COMMON_SHARES"],unit="shares")
cross("H shares",3377482000,hkmain["HK_COMMON_SHARES"],unit="shares")
for field,value,key in [
    ("September deposits over three months",57947,"短期存款"),
    ("September restricted deposits",15472,"受限制存款及现金"),
    ("September current borrowings",79462,"短期贷款"),
    ("September noncurrent borrowings",76040,"长期贷款"),
    ("September current lease",181,"融资租赁负债(流动)"),
    ("September noncurrent lease",1087,"融资租赁负债(非流动)"),
]: cross(field,value,hkbs[key]/1000000)

annual = []
revenue=[335969,346834,345951,339788,294916]
cost=[224389,210736,221198,223923,191465]
op=[78079,98468,89281,87082,75532]
profit=[50127,69709,57756,55805,52849]
ifrs_profit=[51314,73090,62699,59544,54218]
cfos=[94350,109734,89687,91086,75059]
caps=[23638,28684,37084,37708,48398]
cash_equivalents=[156706,131458,108174,66413,23288]
for n,y in enumerate(range(2021,2026)):
    row={"year":y,"cas_revenue_2025_report_basis":revenue[n],"cas_cost_2025_report_basis":cost[n],"cas_gross_profit":revenue[n]-cost[n],"cas_gross_margin_pct":str(Decimal(revenue[n]-cost[n])/Decimal(revenue[n])*100),"cas_operating_profit":op[n],"cas_operating_margin_pct":str(Decimal(op[n])/Decimal(revenue[n])*100),"cas_parent_profit":profit[n],"ifrs_parent_profit_2025_report_basis":ifrs_profit[n],"cfo_historical_report_basis":cfos[n],"cash_capex_historical_report_basis":caps[n],"group_cfo_less_capex":cfos[n]-caps[n],"cash_equivalents":cash_equivalents[n]}
    annual.append(row)
    hist_cf=next(d for d in json.loads((BASE / "financials-eastmoney-cashflow.json").read_text())["result"]["data"] if d["REPORT_DATE"].startswith(str(y)+"-12-31"))
    hist_inc=next(d for d in json.loads((BASE / "financials-eastmoney-income.json").read_text())["result"]["data"] if d["REPORT_DATE"].startswith(str(y)+"-12-31"))
    cross(f"FY{y} CFO historical scope",cfos[n],hist_cf["NETCASH_OPERATE"]/1000000)
    cross(f"FY{y} cash capex historical scope",caps[n],hist_cf["CONSTRUCT_LONG_ASSET"]/1000000)
    cross(f"FY{y} cash equivalents historical scope",cash_equivalents[n],hist_cf["END_CCE"]/1000000)
    cross(f"FY{y} CAS profit restatement difference",profit[n],hist_inc["PARENT_NETPROFIT"]/1000000)
    run("calc","--expr",f"({revenue[n]}-{cost[n]})/{revenue[n]}*100")
    run("calc","--expr",f"{op[n]}/{revenue[n]}*100")
    run("calc","--expr",f"{cfos[n]}-{caps[n]}")

expressions={
    "IFRS_9M_profit_growth_pct":"(47317/46336-1)*100",
    "CAS_9M_profit_growth_pct":"(44403/42780-1)*100",
    "Q3_CFO":"92700-54664", "Q3_cash_capex":"47181-29579",
    "Q3_group_FCF":"92700-54664-47181+29579",
    "Q3_CAS_profit":"44403-28715", "Q3_IFRS_profit":"47317-31054",
    "Q3_IFRS_profit_growth_pct":"((47317-31054)/(46336-30478)-1)*100",
    "CAS_9M_gross_profit":"296031-192458",
    "CAS_9M_gross_margin_pct":"(296031-192458)/296031*100",
    "CAS_9M_operating_margin_pct":"70397/296031*100",
    "IFRS_9M_gross_margin_pct":"86746/296031*100",
    "total_borrowings":"79462+76040", "unrestricted_cash_and_deposits":"59755+57947",
    "narrow_net_debt":"79462+76040+181+1087-59755-57947",
    "narrow_net_debt_vs_H1":"39068-34745",
    "cash_composition_check":"59755+57947+15472",
    "9M_group_FCF":"92700-44969-2212",
    "9M_cash_proxy_after_interest_leases_NCI":"92700-47181-3929-19-566-6169",
    "9M_cash_proxy_including_associate_dividends_and_interest":"92700-47181-3929-19-566-6169+2456+1141",
    "annualized_CAS_profit":"44403*4/3", "annualized_IFRS_profit":"47317*4/3",
    "annualized_CAS_EPS_current_shares":"44403*4/3/21689.434304",
    "annualized_IFRS_EPS_current_shares":"47317*4/3/21689.434304",
    "interim_dividend_total":"21689434304*0.98/1000000",
    "2025_CAS_profit_growth_pct":"(52849/55805-1)*100",
    "2025_CFO_to_group_net_profit":"75059/62783",
    "9M_CFO_to_group_net_profit":"92700/54555",
    "cash_pressure_vs_H1":"(92700-47181)-(54664-29579)",
}
for name,expr in expressions.items():
    log.append(name)
    run("calc","--expr",expr)

output={"research_cutoff":"2026-10-23 Asia/Shanghai, after HKEX 20:22 disclosure", "units":"RMB million unless marked EPS or shares", "current_9m_and_september":current,"annual":annual,"cross_validation":checks,"calculation_expressions":expressions,"limitations":["2021-2025 income uses FY2025 restatement boundary; CFO/capex uses respective reporting-date boundaries and is not a consistent-scope growth series.","Current narrow net debt excludes undisclosed factoring balance, long-term payables, mining-right obligations; not a complete economic debt measure.","IFRS cash-flow breakdown excluding aggregate cash capex/CFO/NCI dividends has primary-source verification only.","Restatement conflicts are retained and explained, not averaged."]}
(BASE / "financials-verified.json").write_text(json.dumps(output,ensure_ascii=False,indent=2))
(BASE / "financials-verified-20261023.json").write_text(json.dumps(output,ensure_ascii=False,indent=2))
(BASE / "financials-rigor-verification.txt").write_text("\n".join(log))
print(f"Saved {len(checks)} cross-checks and {len(expressions)} scenario-free exact arithmetic expressions.")
