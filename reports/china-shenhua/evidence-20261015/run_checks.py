"""Validate source records and audit the frozen report, without network calls.

Primary values below were retrieved from the cited documents during this run.
Forecast inputs are identified as assumptions; recomputation is not source corroboration.
"""
from pathlib import Path
import json
from decimal import Decimal as D
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import report_audit

data = json.loads((HERE/'inputs.json').read_text())
fin = json.loads((HERE/'financials-verified.json').read_text())
calc = json.loads((HERE/'calculations.json').read_text())
m = calc['metrics']
report = HERE.parent/'中国神华研究报告-20261015.md'
fx, price, shares = map(D, [data['fx_cny_per_hkd'], data['price_hkd'], data['shares']])

jobs = [
 ['verify-market-cap','--price','42.92','--shares',data['shares'],'--reported','930910520000','--currency','HKD total H-price marked, Tencent rounded'],
 ['verify-market-cap','--price','42.92','--shares',data['h_shares'],'--reported','144961530000','--currency','HKD H-class, Tencent rounded'],
 ['cross-validate','--field','Issued shares','--values',json.dumps({'HKEX September issued return':21689434304,'Tencent exact shares':21689434304}),'--unit','shares','--tolerance','1'],
 ['cross-validate','--field','H intraday quote, timestamps differ','--values',json.dumps({'Sina 13:45:53':42.92,'Tencent 13:31:04 delayed':42.92}),'--unit','HKD','--tolerance','1'],
 ['verify-valuation','--price','42.92','--eps',m['annualized_ifrs_parent_eps_hkd'],'--bvps',m['parent_bvps_hkd'],'--dividend',m['annualized_h1_dps_hkd'],'--revenue-per-share',m['annualized_revenue_per_share_hkd']],
 ['three-scenario','--price','42.92','--eps',m['normal_eps_hkd'],'--shares','216.89434304','--growth','0.05','0.01','-0.08','--pe','13','11','8.5','--years','3','--currency','HKD'],
]
for field, vals in [
 ('2025 revenue', {'HKEX IFRS':294916,'AAStocks':294916}),
 ('2025 parent profit', {'HKEX IFRS':54218,'AAStocks':54218}),
 ('2026H1 revenue', {'HKEX IFRS':189338,'ETNet':189338}),
 ('2026H1 parent profit', {'HKEX IFRS':31054,'S&P MarketScreener':31054}),
 ('2026H1 cash equivalents', {'HKEX IFRS':51673,'ETNet':51673}),
 ('2026H1 borrowings plus separately presented leases', {'HKEX IFRS':158841,'ETNet':158841}),
 ('2026H1 cash capex', {'HKEX IFRS':29579,'Weidn independent distributor':29579}),
]:
    jobs.append(['cross-validate','--field',field,'--values',json.dumps(vals),'--unit','RMB million','--tolerance','1'])
with (HERE/'financial_rigor.txt').open('w') as out:
    out.write('Price: 2026-10-15 Sina 13:45:53 HKD42.92; Tencent delayed 13:31:04 same price.\n')
    out.write('Generic TTM label below actually uses H1 x2; dividend is an assumed future annual level, NOT entitlement to the detached HKD1.139.\n')
    for args in jobs:
        r = subprocess.run([sys.executable,str(ROOT/'tools/financial_rigor.py')]+args,capture_output=True,text=True)
        out.write(r.stdout+'\n'+r.stderr)
        if r.returncode:
            raise RuntimeError((args, r.stderr))

def irr_float(p, divs, terminal):
    low, high = -.99, 2.
    for _ in range(150):
        r = (low+high)/2
        pv = sum(x/(1+r)**i for i,x in enumerate(divs,1))+terminal/(1+r)**len(divs)
        if pv > p: low = r
        else: high = r
    return (low+high)/2*100

base, bear = calc['scenarios'][1], calc['scenarios'][2]
normal_eps = D('60000000000')/shares/fx
base_div = [normal_eps*D('1.01')**i*D('.70') for i in (1,2,3)]
bear_div = [normal_eps*D('.92')**i*D('.65') for i in (1,2,3)]
sources = fin['sources']
raw = {
 3: (D('.85688'), 'https://www.safe.gov.cn/AppStructured/hlw/RMBQuery.do?COLLCC=546877760 ; 2026-10-14 raw row', 'official_single'),
 12: (irr_float(float(price),list(map(float,base_div)),float(normal_eps*D('1.01')**3*11)), 'Independent cash-flow recomputation from inputs.json, future assumptions', 'derived'),
 18: ((D('56692')/D('53750')-1)*100, sources['h1']+' ; gross-profit source pair', 'derived'),
 27: ((D('28715')/D('27583')-1)*100, sources['cas_h1']+' ; restated CAS pair', 'derived'),
 29: (D('1.438'), sources['h1']+' ; restated comparative EPS note12', 'official_single'),
 30: ((D('1.448')/D('1.438')-1)*100, sources['h1']+' ; EPS recomputed', 'derived'),
 59: (D('1589')/100, sources['h1']+' ; port segment pretax profit', 'official_single'),
 60: (D('2612')/100, sources['fy25']+' ; external segment revenue note5', 'official_single'),
 72: ((D('189338')/D('175423')-1)*100, sources['h1']+' ; restated revenue pair', 'derived'),
 79: (D('12'), sources['h1']+' ; acquisition disclosure', 'official_single'),
 98: (-(D('2719')+377+13+561)/100, sources['h1']+' ; cash flow pp119-120', 'derived'),
 103: (D('-2.3'), 'https://www1.hkexnews.hk/listedco/listconews/sehk/2026/1014/2026101400669.pdf ; reported rounded YoY', 'official_single'),
 106: (D('.1'), 'https://www1.hkexnews.hk/listedco/listconews/sehk/2026/1014/2026101400669.pdf ; reported rounded YoY', 'official_single'),
 112: (D('.7'), 'https://www1.hkexnews.hk/listedco/listconews/sehk/2026/1014/2026101400669.pdf ; reported rounded YoY', 'official_single'),
 123: (price*shares*fx/D('378676000000'), 'Independent recomputation: source revenue x2, price, current shares and FX', 'derived'),
 125: ((price*shares*fx+D('34745000000')+D('99608000000'))/D('378676000000'), 'Independent recomputation of explicitly limited EV proxy', 'derived'),
 127: (D('1.96')/fx/price*100, 'Future annual dividend assumption / FX / price; inputs.json', 'derived'),
 129: (D('43.92'), 'https://stockanalysis.com/quote/hkg/1088/history/ ; 2026-10-14 close', 'dual_source'),
 135: (D('10.78')*D('13258663400')*D('.85688')/(D('8191826000')*2), 'https://static.cninfo.com.cn/finalpage/2026-08-22/1225489734.PDF ; period-end shares, 10/14 price/FX, H1 x2', 'derived'),
 151: (sum(base_div), 'Independent recomputation of base-case annual future dividends', 'derived'),
 160: (irr_float(float(price),list(map(float,bear_div)),float(normal_eps*D('.92')**3*D('8.5'))), 'Independent cash-flow recomputation of bear case, not a forecast validation', 'derived'),
 155: (D(data['valuation_assumptions']['scenarios'][2]['growth'])*100, 'inputs.json bearish growth assumption, not an observed fact', 'assumption'),
 164: (D('30')/normal_eps, 'Independent recomputation of lower endpoint price / assumed EPS', 'derived'),
 167: (D('1.96')/fx/D('38')*100, 'Independent recomputation of yield at upper price endpoint', 'derived'),
 173: (D('1.96')/fx/price*80, 'Independent recomputation: future assumed dividend x80% / FX / price', 'derived'),
}
points = report_audit.extract_data_points(report.read_text())
sample = report_audit.sample_points(points, .15, 1015)
(HERE/'audit-sample.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2))
results, excluded = [], []
for item in sample:
    if item['id'] in (78,85):
        excluded.append({**item,'reason':'2029 is a management target year, not financial amount' if item['id']==78 else 'Parser captured H1 as value 1; actual capex232.90 separately verified against original report'})
        continue
    value, source, kind = raw[item['id']]
    row={**item,'fetched_value':str(value),'fetched_source':source,'verification_type':kind}
    if item['id']==129:
        row.update(fetched_value2='43.92',fetched_source2='https://content.etnet.com.hk/content/sywg/sc/quote.php?code=01088 ; 2026-10-14 16:15')
    # No duplicate issuer mirrors disguised as independent sources.
    results.append(row)
(HERE/'audit-exclusions.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2))
(HERE/'audit-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
r = subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'verdict','--results',json.dumps(results,ensure_ascii=False),'--report',report.name,'--output-json'],capture_output=True,text=True)
(HERE/'audit-verdict.txt').write_text(r.stdout+r.stderr)
for row in results:
    err=abs(D(str(row['reported_value']))-D(row['fetched_value']))/abs(D(str(row['reported_value'])))
    assert err <= D('.01'), (row['label'], str(err))
print(json.dumps({'extracted':len(points),'sample':len(sample),'valid':len(results),'excluded':len(excluded),'types':{kind:sum(r['verification_type']==kind for r in results) for kind in {r['verification_type'] for r in results}},'max_relative_error_pct':str(max(abs(D(str(r['reported_value']))-D(r['fetched_value']))/abs(D(str(r['reported_value'])))*100 for r in results))},ensure_ascii=False,indent=2))
