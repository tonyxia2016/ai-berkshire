from decimal import Decimal, getcontext
from pathlib import Path
import json
import subprocess

getcontext().prec = 32
D = Decimal
base = Path(__file__).resolve().parent
root = base.parents[2]
tool = root / 'tools' / 'financial_rigor.py'
price, apr, fx = D('39.62'), D('50.20'), D('0.85696')
total, hs = D('21689434304'), D('3377482000')
ashares = total - hs
market = {
    'date': '2026-10-23',
    'h_price_hkd': price,
    'a_price_cny': apr,
    'fx_cny_per_hkd_official_midpoint': fx,
    'fx_hkd_per_cny_official_midpoint': 1 / fx,
    'total_issued_shares': total,
    'h_shares': hs,
    'a_shares': ashares,
    'h_price_cny': price * fx,
    'h_class_market_cap_hkd': price * hs,
    'all_shares_marked_at_h_price_hkd': price * total,
    'all_shares_marked_at_h_price_cny': price * total * fx,
    'a_plus_h_market_cap_cny': apr * ashares + price * hs * fx,
    'a_plus_h_market_cap_hkd': apr * ashares / fx + price * hs,
    'a_plus_h_dividend_equalized_market_cap_cny': (apr - D('0.98')) * ashares + price * hs * fx,
    'h_discount_to_a_raw_percent': (1 - price * fx / apr) * 100,
    'h_discount_to_a_adjusted_for_dividend_percent': (1 - price * fx / (apr - D('0.98'))) * 100,
    'latest_two_declared_dps_hkd': D('1.185') + D('1.139'),
    'latest_two_declared_yield_percent': (D('1.185') + D('1.139')) / price * 100,
    'latest_two_declared_20pct_tax_example_yield_percent': (D('1.185') + D('1.139')) * D('0.8') / price * 100,
    'fy2025_dps_cny': D('0.98') + D('1.03'),
    'fy2025_actual_hkd_dps': D('1.074') + D('1.185'),
    'fy2025_actual_hkd_yield_percent': (D('1.074') + D('1.185')) / price * 100,
    'past12months_paid_dps_hkd': D('1.074') + D('1.185'),
    'past12months_ex_date_sum_dps_hkd_warning_three_payments': D('1.074') + D('1.185') + D('1.139'),
    'past12months_ex_date_sum_yield_percent_warning_not_normal_annual_runrate': (D('1.074') + D('1.185') + D('1.139')) / price * 100,
    '2026interim_hkd_unrounded_at_fixed_dividend_fx': D('0.98') * D('1.1621'),
    'investing_a_price_discrepancy_percent': (apr - D('50.14')) / apr * 100,
}

# Uniform period and accounting basis for comparison. Shenhua has since published
# Q3, so this H1 panel is not its latest trading PE and must not be labelled TTM.
data = [
    ['神华', '01088', '39.62', 'HKD', '21689434304', '28715000000', '26895000000', '450933000000', '2.324'],
    ['兖矿', '01171', '10.31', 'HKD', '10036852020', '7149644000', '4607236000', '76858362000', '0.5979'],
    ['中煤', '01898', '9.455', 'HKD', '13258663400', '8149301000', '8543567000', '166185541000', '0.46222'],
    ['陕煤', '601225', '26.29', 'CNY', '9695000000', '11272422101.47', '9736398200', '101138897973.41', '0.967'],
]
peers = []
for name, ticker, p, curr, shares, profit, recurring, eq, dividend in data:
    p, shares, profit, recurring, eq, dividend = map(D, [p, shares, profit, recurring, eq, dividend])
    rate = fx if curr == 'HKD' else D(1)
    eps = profit * 2 / shares / rate
    bps = eq / shares / rate
    peers.append({
        'company': name, 'ticker': ticker, 'price': p, 'currency': curr,
        'price_date': '2026-10-23', 'earnings_period': '2026H1 CAS, annualized by 2',
        'shares_issued': shares, 'half_year_common_profit_cny': profit,
        'half_year_recurring_common_profit_cny': recurring,
        'common_equity_cny': eq, 'annualized_eps_in_price_currency': eps,
        'half_year_earnings_per_current_issued_share_cny': profit / shares,
        'bvps_cny': eq / shares,
        'bvps_in_price_currency': bps,
        'pe_h1_annualized': p / eps,
        'pe_h1_recurring_annualized': p * rate * shares / (recurring * 2),
        'pb_h1': p / bps,
        'latest_two_declared_dps_in_price_currency': dividend,
        'latest_two_declared_yield_percent': dividend / p * 100,
    })

def conv(o):
    if isinstance(o, Decimal): return str(o)
    raise TypeError(type(o).__name__)
latest = []
for name, ticker, basis, p, shares, profit9m, eq in [
    ['神华', '01088', 'CAS', '39.62', '21689434304', '44403000000', '444569000000'],
    ['神华', '01088', 'IFRS', '39.62', '21689434304', '47317000000', '453033000000'],
    ['中煤', '01898', 'CAS', '9.455', '13258663400', '12748798000', '168432937000'],
]:
    p, shares, profit9m, eq = map(D, [p, shares, profit9m, eq])
    annualeps = profit9m * D(4) / D(3) / shares / fx
    bvps = eq / shares / fx
    latest.append({'company':name, 'ticker':ticker, 'basis':basis, 'period':'2026-09-30; 9M annualized by 4/3; not TTM', 'price_hkd':p, 'profit9m_cny':profit9m, 'equity_cny':eq, 'annualized_eps_hkd':annualeps, 'bvps_hkd':bvps, 'pe_9m_annualized':p/annualeps, 'pb_latest':p/bvps})
(base/'market-calculations.json').write_text(json.dumps({'market':market, 'peers':peers, 'latest_9m':latest}, ensure_ascii=False, indent=2, default=conv))

checks = []
def run(label, *args):
    r = subprocess.run(['python3', str(tool), *map(str,args)], capture_output=True, text=True)
    checks.append('\n### '+label+'\nCOMMAND: '+ ' '.join(map(str,args))+'\n'+r.stdout+r.stderr)
    if r.returncode: raise RuntimeError(r.stderr)

run('H price marked total market capitalization', 'verify-market-cap', '--price', price, '--shares', total, '--reported', '859335390000', '--currency', 'HKD')
run('H share class capitalization only', 'verify-market-cap', '--price', price, '--shares', hs, '--reported', '133815840000', '--currency', 'HKD')
for label, vals, unit in [
    ('H close 2026-10-23', {'Sina 16:08:12':39.62,'Tencent 16:08:14':39.62,'etnet 16:15':39.62,'StockAnalysis 16:08':39.62},'HKD'),
    ('A close 2026-10-23', {'Sina 15:34:59':50.20,'Tencent 16:14:52':50.20},'CNY'),
    ('issued total shares', {'HKEX Sep month return':21689434304,'Tencent quote':21689434304},'shares'),
    ('issued H shares', {'HKEX Sep month return':3377482000,'Tencent quote':3377482000},'shares'),
    ('2026 interim declared DPS', {'HKEX update':1.139,'Sina dividend':1.139,'etnet dividend':1.139},'HKD/share'),
    ('Shenhua H1 CAS common profit', {'company H1':28715000000,'THS financial table':28715000000},'CNY'),
    ('Yankuang H1 CAS common profit', {'company H1':7149644000,'THS financial table rounded':7150000000},'CNY'),
    ('Chinacoal H1 CAS common profit', {'company H1':8149301000,'THS financial table rounded':8149000000},'CNY'),
    ('Shaanxicoal H1 CAS common profit', {'company H1':11272422101.47,'THS financial table rounded':11272000000},'CNY'),
]:
    run(label,'cross-validate','--field',label,'--values',json.dumps(vals),'--unit',unit,'--tolerance','1')
for item in peers:
    run(item['company']+' H1 CAS annualized; generic tool TTM label DOES NOT APPLY', 'verify-valuation','--price',item['price'],'--eps',item['annualized_eps_in_price_currency'],'--bvps',item['bvps_in_price_currency'],'--dividend',item['latest_two_declared_dps_in_price_currency'])
for item in latest:
    run(item['company']+' '+item['basis']+' 9M annualized; generic tool TTM label DOES NOT APPLY', 'verify-valuation','--price',item['price_hkd'],'--eps',item['annualized_eps_hkd'],'--bvps',item['bvps_hkd'])
for key, expr in {
    'H marked CNY market cap':'39.62 * 21689434304 * 0.85696',
    'A plus H actual CNY market cap':'50.20 * 18311952304 + 39.62 * 3377482000 * 0.85696',
    'Raw H discount percent':'(1 - 39.62 * 0.85696 / 50.20) * 100',
    'Dividend-adjusted H discount percent':'(1 - 39.62 * 0.85696 / (50.20 - 0.98)) * 100',
    'Last12month paid dividend yield percent':'(1.074 + 1.185) / 39.62 * 100',
    'Last12month exdate dividend yield not annual runrate':'(1.074 + 1.185 + 1.139) / 39.62 * 100',
}.items():
    run(key,'calc','--expr',expr)
(base/'market-financial-rigor.txt').write_text('All valuation inputs use exact Decimal arithmetic in market-calculate.py. financial_rigor calc may retain binary float tails; JSON Decimal outputs are authoritative.\n' + ''.join(checks))
print(json.dumps({'market':market,'peers':peers,'latest_9m':latest},ensure_ascii=False,indent=2,default=conv))
