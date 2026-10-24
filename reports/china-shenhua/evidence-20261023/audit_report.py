"""Reproduce the fixed-seed report sample against saved source records.

Single-issuer operational facts are labelled as such; arithmetic checks do not
claim to be independent validation of valuation assumptions.
"""
from pathlib import Path
from decimal import getcontext
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPORT = HERE.parent / '中国神华研究报告-20261023.md'
sys.path.insert(0, str(ROOT / 'tools'))
from financial_rigor import exact as D
from report_audit import extract_data_points, sample_points
getcontext().prec = 42

def load(name):
    return json.loads((HERE / name).read_text())

def rows(name):
    return load(name)['result']['data']

def row_at(name, period):
    return next(r for r in rows(name) if r['REPORT_DATE'].startswith(period))

def source_number(name, anchor, token):
    lines = (HERE / name).read_text().splitlines()
    found = [(i + 1, line) for i, line in enumerate(lines)
             if anchor in line and token in line]
    assert found, (name, anchor, token)
    line_no, line = found[0]
    evidence.append({'file': name, 'line': line_no, 'text': line.strip(),
                     'selected_number': token})
    return D(token.replace(',', ''))

def quote(source, ticker):
    raw = snapshots['sources'][source]['text']
    if source == 'sina':
        text = re.search(r'hq_str_rt_hk' + ticker + r'="([^"]+)', raw)[1]
        return D(text.split(',')[6])
    text = re.search(r'v_hk' + ticker + r'="([^"]+)', raw)[1]
    return D(text.split('~')[3])

evidence = []
snapshots = load('market-live-snapshots.json')
cas = 'business-q3-2026.txt'
ifrs = 'business-q3-2026-hk.txt'
em_cas = 'financials-eastmoney-main.json'
em_hk = 'financials-RPT_HKF10_FN_MAININDICATOR.json'
latest = row_at(em_hk, '2026-09')
balance = {r['ITEM_NAME']: D(str(r['AMOUNT'])) for r in
           rows('financials-RPT_HKF10_FN_BALANCE.json')
           if r['REPORT_DATE'].startswith('2026-09')}
fy = D('100000000')
fx = D(load('inputs.json')['fx_cny_per_hkd'])
price = quote('sina', '01088')
assert price == quote('tencent', '01088')
hs = source_number('shenhua-202609-shares.txt', '本月底結存', '3,377,482,000')
ashares = source_number('shenhua-202609-shares.txt', '本月底結存', '18,311,952,304')
shares = hs + ashares
cash = source_number(ifrs, '現金及現金等價物', '59,755')
term = source_number(ifrs, '定期存款', '57,947')
restricted = source_number(ifrs, '受限制', '15,472')
borrow_interest = source_number(ifrs, '支付利息', '3,929')
lease_interest = source_number(ifrs, '已付租金之利息部分', '19')
lease_principal = source_number(ifrs, '已付租金之資本部分', '566')

values = {}
def add(i, value, source, kind, value2=None, source2='', note=''):
    values[i] = {'fetched_value': float(value), 'fetched_source': source,
                 'fetched_value_exact': str(value), 'validation_kind': kind,
                 'fetched_value2': None if value2 is None else float(value2),
                 'fetched_source2': source2, 'scope_note': note}

add(6, source_number(cas, '42,808', '38,704') / 100,
    'CAS三季报，2025年前三季度重述扣非利润', 'primary_and_vendor',
    D(str(row_at(em_cas, '2025-09')['KCFJCXSYJLR'])) / fy, '东方财富CAS结构化数据')
add(12, source_number(ifrs, '基本（人民幣元）', '2.187'),
    'IFRS三季报，比较期每股盈利', 'primary_and_vendor',
    D(str(row_at(em_hk, '2025-09')['BASIC_EPS'])), '东方财富IFRS结构化数据')
add(20, source_number(cas, '营业收入', '96,228') / 100,
    'CAS三季报，单Q3重述收入', 'primary_only', note='同一发行人的CAS及IFRS公告不计独立双源')
add(37, source_number(cas, '利润总额', '11,183') / 100,
    'CAS三季报，铁路分部利润', 'primary_only')
add(52, source_number(cas, '电煤中长期', '311.4') / 100,
    'CAS三季报，百万吨换算为亿吨', 'primary_only')
add(53, source_number(cas, '合计/加权', '370'),
    'CAS三季报，前三季度售电均价', 'primary_only')
add(62, shares / fy, 'HKEX九月月报，A与H已发行股份相加', 'primary_and_vendor',
    D(str(latest['ISSUED_COMMON_SHARES'])) / fy, '东方财富港股最新股数')
add(65, cash / 100, 'IFRS三季报现金等价物', 'primary_and_vendor',
    D(str(latest['END_CASH'])) / fy, '东方财富港股现金等价物')
add(67, (cash + term) / 100, 'IFRS现金等价物加三个月以上定存', 'derived_verified_inputs',
    (balance['现金及等价物'] + balance['短期存款']) / fy, '东方财富港股报表对应两项合计')
add(68, restricted / 100, 'IFRS三季报受限存款', 'primary_and_vendor',
    balance['受限制存款及现金'] / fy, '东方财富港股报表')
add(76, -(borrow_interest + lease_interest + lease_principal) / 100,
    'IFRS现金流三项支付合计', 'derived_primary_inputs')
add(80, price * hs / fy, '新浪收盘价乘HKEX已发行H股数', 'derived_verified_inputs',
    D(str(latest['HKSK_MARKET_CAP'])) / fy, '东方财富H类别市值')
add(89, price * fx * shares / D(str(latest['TOTAL_PARENT_EQUITY'])),
    '重算：股价×汇率×股数÷IFRS归母权益', 'derived_verified_inputs')
cas_profit = source_number(cas, '44,403', '44,403')
cas_equity = source_number(cas, '444,569', '444,569')
add(91, cas_profit * 4 / 3 / cas_equity * 100,
    '重算：CAS九月利润×4/3÷期末归母权益', 'derived_verified_inputs')
add(94, D('1.96') / fx / price * 100,
    '重算：假设年息÷汇率÷股价', 'assumption_arithmetic', note='1.96元是水平假设，不是公司承诺')
peers = {r['ticker']: r for r in load('market-calculations.json')['peers']}
sh_profit = source_number('business-h1-2026.txt', '28,715', '28,715') * D('1000000')
add(97, price * fx * shares / (sh_profit * 2),
    '重算：现价及最新股数÷CAS中报利润的两倍', 'derived_verified_inputs')
cc = peers['01898']
cc_equity = source_number('chinacoal-2026H1-cn.txt', '归属于上市公司股东的净资产', '166,185,541') * 1000
add(103, quote('sina', '01898') * fx * D(cc['shares_issued']) / cc_equity,
    '重算：中煤中报普通股权益、最新股数及收盘价', 'derived_primary_inputs')
yk = peers['01171']
yk_profit = source_number('yankuang-2026H1-sina.txt', '7,149,644', '7,149,644') * 1000
add(105, quote('sina', '01171') * fx * D(yk['shares_issued']) / (yk_profit * 2),
    '重算：兖矿中报CAS归母利润、最新股数及收盘价', 'derived_primary_inputs')
add(104, quote('sina', '01171'), '新浪港股收盘行情', 'two_market_vendors',
    quote('tencent', '01171'), '腾讯港股收盘行情')

# Independently reconstruct the equity DCF, without reading model.py results.
cf = D('55000000000') / shares / fx
discount, growth = D('0.10'), D('0.01')
dcf_value = sum(cf * (1 + growth) ** t / (1 + discount) ** t for t in range(1, 11))
dcf_value += cf * (1 + growth) ** 10 / discount / (1 + discount) ** 10
add(117, dcf_value, '独立Decimal重算：十年1%增长、终值零增长、10%折现', 'assumption_arithmetic')
eps = D('60000000000') / shares / fx
dividends = [eps * D('0.92') ** t * D('0.65') for t in (1, 2, 3)]
exit_price = eps * D('0.92') ** 3 * D('8.5')
lo, hi = D('-0.9'), D('1')
for _ in range(180):
    mid = (lo + hi) / 2
    npv = sum(dividends[t-1] / (1+mid) ** t for t in (1, 2, 3)) + exit_price / (1+mid) ** 3 - price
    if npv > 0:
        lo = mid
    else:
        hi = mid
add(137, (lo + hi) / 2 * 100,
    '独立Decimal现金流IRR：-8%增长、8.5倍退出、65%派息', 'assumption_arithmetic')
add(144, D('1.96') / fx / 38 * 100,
    '重算：价格区间38港元端点的股息率', 'assumption_arithmetic',
    note='另检查33港元端点，6.9307666815%应显示6.93%；抽样器只抽区间第一个数字')
assert round(D('1.96') / fx / 33 * 100, 2) == D('6.93')
add(147, 48 / eps, '重算：48港元÷600亿元正常利润对应每股盈利', 'assumption_arithmetic')

all_points = extract_data_points(REPORT.read_text())
sample = sample_points(all_points, ratio=0.15, seed=20261023)
assert {p['id'] for p in sample} == set(values), 'Report sample changed; review new sample before approving.'
results = [{**p, **values[p['id']]} for p in sample]
for item in results:
    reported = D(str(item['reported_value']))
    for field in ('fetched_value', 'fetched_value2'):
        if item.get(field) is not None:
            assert abs(D(str(item[field])) - reported) / abs(reported) <= D('0.01'), item
for name, payload in [('audit-sample.json', sample), ('audit-results.json', results),
                      ('audit-source-excerpts.json', evidence)]:
    (HERE / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
extract = subprocess.run([sys.executable, str(ROOT/'tools/report_audit.py'), 'extract',
                          '--report', str(REPORT), '--seed', '20261023'],
                         capture_output=True, text=True, check=True)
(HERE/'audit-extract.txt').write_text(extract.stdout)
verdict = subprocess.run([sys.executable, str(ROOT/'tools/report_audit.py'), 'verdict',
                          '--report', str(REPORT), '--results', json.dumps(results, ensure_ascii=False),
                          '--output-json'], capture_output=True, text=True, check=True)
(HERE/'audit-verdict.txt').write_text(verdict.stdout)
outcome = json.loads(verdict.stdout[verdict.stdout.rfind('\n{') + 1:])
assert outcome['pass_count'] == len(sample) and outcome['warn_count'] == 0 and outcome['fail_count'] == 0
(HERE/'audit-verdict.json').write_text(json.dumps(outcome, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'extracted_points': len(all_points), 'sample_size': len(sample), **outcome}, ensure_ascii=False))
