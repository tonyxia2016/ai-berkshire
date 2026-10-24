"""Dated research arithmetic; all calculations use financial_rigor.exact/Decimal.

CAS is the primary earnings basis. Nine-month annualization is not TTM.
Net debt and EV proxies do not assert a fully reconciled financing balance.
Group CFO less asset payments is not cash attributable to ordinary shareholders.
"""
from decimal import getcontext
from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from financial_rigor import exact as D
getcontext().prec = 42
data = json.loads((HERE / 'inputs.json').read_text())
p, ap, fx, shares, hs = (D(data[k]) for k in ('price_hkd','a_price_cny','fx_cny_per_hkd','shares','h_shares'))
mm = D('1000000')
yi = D('100000000')
q = {k:D(v) for k,v in data['q3'].items()}
h = {k:D(v) for k,v in data['h1'].items()}
ic = {k:D(v) for k,v in data['ifrs_cash'].items()}
d = {k:D(v) for k,v in data['dividends'].items()}
a = data['valuation_assumptions']
annualize = D(4)/3

def change(x,y):
    return (x/y-1)*100

def dcf(cf,g,r,terminal=D(0),years=10):
    cash = [cf*(1+g)**t for t in range(1,years+1)]
    return sum(v/(1+r)**t for t,v in enumerate(cash,1)) + cash[-1]*(1+terminal)/(r-terminal)/(1+r)**years

def solve_growth(cf,r):
    lo,hi=D('-0.50'),D('0.50')
    for _ in range(180):
        mid=(lo+hi)/2
        if dcf(cf,mid,r)>p: hi=mid
        else: lo=mid
    return (lo+hi)/2

def irr(entry,divs,exit_price):
    lo,hi=D('-0.99'),D(2)
    for _ in range(180):
        mid=(lo+hi)/2
        pv=sum(v/(1+mid)**t for t,v in enumerate(divs,1))+exit_price/(1+mid)**len(divs)
        if pv>entry: lo=mid
        else: hi=mid
    return (lo+hi)/2

m = {
 'h_price_cny':p*fx,
 'h_class_cap_hkd_yi':p*hs/yi,
 'h_marked_total_cap_hkd_yi':p*shares/yi,
 'h_marked_total_cap_cny_yi':p*shares*fx/yi,
 'mixed_ah_cap_cny_yi':(ap*(shares-hs)+p*fx*hs)/yi,
 'raw_h_discount_pct':(1-p*fx/ap)*100,
 'dividend_right_adjusted_h_discount_pct':(1-p*fx/(ap-d['current_interim_cny']))*100,
 'share_count_increase_pct':change(shares,D(data['old_shares'])),
 'cas_9m_annualized_profit_yi':q['cas_profit_mm']*annualize/100,
 'ifrs_9m_annualized_profit_yi':q['ifrs_profit_mm']*annualize/100,
 'recurring_cas_9m_annualized_profit_yi':q['recurring_cas_profit_mm']*annualize/100,
 'cas_q3_annualized_profit_yi':q['single_quarter_cas_profit_mm']*4/100,
 'cas_9m_annualized_eps_cny':q['cas_profit_mm']*annualize*mm/shares,
 'cas_9m_annualized_eps_hkd':q['cas_profit_mm']*annualize*mm/shares/fx,
 'ifrs_9m_annualized_eps_hkd':q['ifrs_profit_mm']*annualize*mm/shares/fx,
 'cas_bvps_hkd':q['cas_parent_equity_mm']*mm/shares/fx,
 'ifrs_bvps_hkd':q['ifrs_parent_equity_mm']*mm/shares/fx,
 'revenue_annualized_per_share_hkd':q['revenue_mm']*annualize*mm/shares/fx,
 'cas_gross_margin_pct':(q['revenue_mm']-q['cost_mm'])/q['revenue_mm']*100,
 'cas_prior_gross_margin_pct':(q['prior_revenue_mm']-q['prior_cost_mm'])/q['prior_revenue_mm']*100,
 'cas_operating_margin_pct':q['operating_profit_mm']/q['revenue_mm']*100,
 'cas_annualized_roe_closing_equity_pct':q['cas_profit_mm']*annualize/q['cas_parent_equity_mm']*100,
 'leverage_pct':q['total_liabilities_mm']/q['total_assets_mm']*100,
 'group_fcf_mm':q['cfo_mm']-q['cash_capex_mm'],
 'prior_group_fcf_mm':q['prior_cfo_mm']-q['prior_cash_capex_mm'],
 'h1_group_fcf_mm':h['cfo_mm']-h['cash_capex_mm'],
 'q3_cfo_mm':q['cfo_mm']-h['cfo_mm'],
 'q3_cash_capex_mm':q['cash_capex_mm']-h['cash_capex_mm'],
 'borrowing_floor_mm':q['short_borrowings_mm']+q['long_borrowings_mm'],
 'mixed_debt_proxy_mm':q['short_borrowings_mm']+q['long_borrowings_mm']+q['maturing_noncurrent_liabilities_mm']+q['noncurrent_leases_mm'],
 'working_capital_contract_increase_mm':q['contract_liabilities_mm']-q['prior_contract_liabilities_mm'],
 'working_capital_salary_increase_mm':q['employee_payable_mm']-q['prior_employee_payable_mm'],
 'last_two_declared_dps_hkd':d['last_final_hkd']+d['current_interim_hkd'],
 'forward_level_dps_hkd':d['forward_level_assumption_cny']/fx,
 'interim_dividend_total_yi':d['current_interim_cny']*shares/yi,
 'normal_eps_hkd':D(a['normal_cas_profit_mm'])*mm/shares/fx
}
for key in ['revenue','cas_profit','ifrs_profit','recurring_cas_profit','cfo','cash_capex','finance_expense','reported_eps_cny','single_quarter_revenue','single_quarter_cas_profit','single_quarter_eps_cny']:
    k=key if key.endswith('_cny') else key+'_mm'
    m[key+'_growth_pct']=change(q[k],q['prior_'+k])
m['group_fcf_growth_pct']=change(m['group_fcf_mm'],m['prior_group_fcf_mm'])
m['q3_group_fcf_mm']=m['q3_cfo_mm']-m['q3_cash_capex_mm']
m['net_debt_floor_proxy_mm']=m['borrowing_floor_mm']-q['cash_mm']
m['mixed_net_debt_proxy_mm']=m['mixed_debt_proxy_mm']-q['cash_mm']
m['cas_pe_9m_annualized']=p/m['cas_9m_annualized_eps_hkd']
m['ifrs_pe_9m_annualized']=p/m['ifrs_9m_annualized_eps_hkd']
m['cas_pb']=p/m['cas_bvps_hkd']
m['ifrs_pb']=p/m['ifrs_bvps_hkd']
m['ps_9m_annualized']=p/m['revenue_annualized_per_share_hkd']
m['group_fcf_annualized_yield_pct']=m['group_fcf_mm']*annualize*mm/(p*shares*fx)*100
m['group_fcf_annualized_per_share_hkd']=m['group_fcf_mm']*annualize*mm/shares/fx
m['historical_declared_yield_pct']=m['last_two_declared_dps_hkd']/p*100
m['forward_level_yield_pct']=m['forward_level_dps_hkd']/p*100
m['forward_level_after20_yield_pct']=m['forward_level_yield_pct']*D('0.8')
m['normal_pe']=p/m['normal_eps_hkd']
m['normal_value_10pe_hkd']=m['normal_eps_hkd']*10
m['normal_value_12pe_hkd']=m['normal_eps_hkd']*12
m['ev_proxy_low_to_sales']=(p*shares*fx/mm+m['net_debt_floor_proxy_mm']+q['nci_equity_mm'])/(q['revenue_mm']*annualize)
m['ev_proxy_high_to_sales']=(p*shares*fx/mm+m['mixed_net_debt_proxy_mm']+q['nci_equity_mm'])/(q['revenue_mm']*annualize)
m['nonrestricted_cash_mm']=ic['cash_equivalents_mm']+ic['term_deposits_mm']
m['borrowings_mm']=ic['current_borrowings_mm']+ic['noncurrent_borrowings_mm']
m['narrow_net_debt_mm']=m['borrowings_mm']+ic['current_leases_mm']+ic['noncurrent_leases_mm']-m['nonrestricted_cash_mm']
m['narrow_net_debt_change_from_h1_mm']=m['narrow_net_debt_mm']-D('34745')
m['cash_pressure_bridge_mm']=m['group_fcf_mm']-ic['interest_paid_mm']-ic['lease_interest_mm']-ic['lease_principal_mm']-ic['nci_dividends_paid_mm']+ic['associate_dividends_received_mm']+ic['interest_received_mm']
m['cash_pressure_bridge_annualized_mm']=m['cash_pressure_bridge_mm']*annualize
m['nci_unpaid_profit_mm']=ic['nci_profit_mm']-ic['nci_dividends_paid_mm']
m['cash_pressure_with_nci_profit_proxy_annualized_mm']=(m['cash_pressure_bridge_mm']-m['nci_unpaid_profit_mm'])*annualize
m['ev_including_dividends_proxy_to_sales']=(p*shares*fx/mm+m['narrow_net_debt_mm']+ic['nci_equity_mm']+q['dividends_payable_mm'])/(q['revenue_mm']*annualize)
m['ifrs_reported_eps_growth_pct']=change(ic['reported_eps_cny'],ic['prior_reported_eps_cny'])
m['ifrs_q3_reported_eps_growth_pct']=change(ic['q3_reported_eps_cny'],ic['prior_q3_reported_eps_cny'])
segments=[]
for row in data['segments_9m']:
    r={k:D(v) for k,v in row.items() if k!='name'}
    segments.append({**row,'gross_margin_pct':(r['revenue_mm']-r['cost_mm'])/r['revenue_mm']*100,
       'revenue_growth_pct':change(r['revenue_mm'],r['prior_revenue_mm']),
       'pbt_change_yi':(r['pbt_mm']-r['prior_pbt_mm'])/100})

cashvalues=[]
for cfmm in a['owner_cashflow_mm']:
    cf=D(cfmm)*mm/shares/fx
    for rstr in a['discount_rates']:
        r=D(rstr)
        cashvalues.append({'owner_cash_yi':D(cfmm)/100,'discount':r,'value_hkd':dcf(cf,D(a['dcf_growth']),r),
           'implied_growth_pct':solve_growth(cf,r)*100,'cash_yield_pct':cf/p*100})

scenarios=[]
for row in a['scenarios']:
    g,pe,payout=(D(row[k]) for k in ('growth','exit_pe','payout'))
    eps=m['normal_eps_hkd']
    divs=[eps*(1+g)**t*payout for t in (1,2,3)]
    target=eps*(1+g)**3*pe
    scenarios.append({**row,'target_hkd':target,'dividends_hkd':divs,'total_dividends_hkd':sum(divs),
       'total_return_pct':((target+sum(divs))/p-1)*100,'irr_pct':irr(p,divs,target)*100,
       'irr_after20_pct':irr(p,[v*D('0.8') for v in divs],target)*100,
       'entry_for10_hkd':sum(v/D('1.1')**t for t,v in enumerate(divs,1))+target/D('1.1')**3})
base=scenarios[1]
bands=[{'price_hkd':D(x),'normal_pe':D(x)/m['normal_eps_hkd'],
        'forward_level_yield_pct':m['forward_level_dps_hkd']/D(x)*100,
        'base_irr_pct':irr(D(x),base['dividends_hkd'],base['target_hkd'])*100} for x in ('30','33','38','39.62','48')]
m['base_no_multiple_compression_irr_pct']=irr(p,base['dividends_hkd'],m['normal_eps_hkd']*D('1.01')**3*m['normal_pe'])*100
m['low_hurdle_value_hkd']=dcf(D('55000')*mm/shares/fx,D('0.01'),D('0.07'))
result={'metrics':m,'segments_9m':segments,'dcf':cashvalues,'scenarios':scenarios,'price_bands':bands}
(HERE/'calculations.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str)+'\n')

def run(args):
    cp=subprocess.run([sys.executable,str(ROOT/'tools/financial_rigor.py'),*map(str,args)],capture_output=True,text=True,check=True)
    return cp.stdout

logs=[run(['verify-market-cap','--price',p,'--shares',shares,'--reported',data['reported_h_marked_total_marketcap_hkd'],'--currency','HKD'])]
logs.append(run(['verify-market-cap','--price',p,'--shares',hs,'--reported',data['reported_h_marketcap_hkd'],'--currency','HKD']))
logs.append('Inputs below are nine-month annualized CAS EPS and group CFO less asset payments; generic tool TTM/FCF labels do not change these definitions.\n')
logs.append(run(['verify-valuation','--price',p,'--eps',m['cas_9m_annualized_eps_hkd'],'--bvps',m['cas_bvps_hkd'],
   '--fcf-per-share',m['group_fcf_annualized_per_share_hkd'],'--dividend',m['forward_level_dps_hkd'],'--revenue-per-share',m['revenue_annualized_per_share_hkd']]))
logs.append(run(['three-scenario','--price',p,'--eps',m['normal_eps_hkd'],'--shares',shares/yi,'--growth','0.05','0.01','-0.08','--pe','13','11','8.5','--years','3','--currency','HKD']))
(HERE/'financial_rigor.txt').write_text('\n'.join(logs))
print(json.dumps(result,ensure_ascii=False,indent=2,default=str))
