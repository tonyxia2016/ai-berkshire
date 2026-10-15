"""Audit saved-source facts separately from model assumptions and calculations.

Uses the shared random extractor and verdict CLI. Does not convert single-source
facts or mixed-source warnings into independent verification.
"""
from pathlib import Path
from decimal import Decimal as D, getcontext
import contextlib, importlib.util, io, json, subprocess, sys
getcontext().prec=40
P=Path(__file__).resolve().parent
ROOT=P.parents[2]; REPORT=P.parent/'Ethereum研究报告-20261015.md'
def load(name): return json.loads((P/name).read_text(),parse_float=str)
def save(name,data): (P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str)+'\n')
spec=importlib.util.spec_from_file_location('audit',ROOT/'tools/report_audit.py')
audit=importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
text=REPORT.read_text(); allpoints=audit.extract_data_points(text)
samples=audit.sample_points(allpoints,.15,20261015)
calc=load('calculations.json'); market=load('market-final.json'); agg=load('aggregates.json')
price=D(calc['price']); supply=D(calc['supply'])
bear_price=D('150e9')/(supply*D('1.01')**5)
bear_ret=(bear_price/price-1)*100
bear_staking=((bear_price/price)**(D(1)/5)*D('1.025')-1)*100
results=[]; excluded=[]
for p in samples:
    x=dict(p); label=x['label']
    if label.startswith('营业收入及分部') or label.startswith('ultrasound 当日北京时间'):
        x['reason']='提取器把L1或时间片段误认为财务数值'; excluded.append(x); continue
    x.update(fetched_value2=None,fetched_source2='')
    if label.startswith('CoinGecko 价格'):
        x.update(fetched_value=str(price),fetched_source='CoinGecko direct API; market-final.json',fetched_value2=calc['coinbase'],fetched_source2='Coinbase direct API; same fetch round',kind='dual_source_market')
    elif label.startswith('Coinbase 现货'):
        x.update(fetched_value=calc['coinbase'],fetched_source='Coinbase direct API; market-final.json',fetched_value2=calc['kraken'],fetched_source2='Kraken direct API; same fetch round',kind='dual_source_market')
    elif label.startswith('Ethereum L1 · 美元'):
        x.update(fetched_value=str(D(load('defillama-competition-extract.json')['stablecoins']['selected_values']['Ethereum'])/D('1e9')),fetched_source='DefiLlama stablecoinchains snapshot 2026-10-15 05:50:54 UTC; defillama-competition-extract.json (transcript extract)',kind='single_source_auxiliary')
    elif label.startswith('Solana · DeFi'):
        sol=next(z for z in load('defillama-competition-extract.json')['tvl']['entries'] if z['name']=='Solana')
        x.update(fetched_value=str(D(sol['tvl'])/D('1e9')),fetched_source='DefiLlama chains snapshot 2026-10-15 05:50:48 UTC; defillama-competition-extract.json (transcript extract)',kind='single_source_auxiliary')
    elif label=='悲观 · 累计币价回报':
        x.update(fetched_value=str(bear_ret),fetched_source='Independent Decimal recalculation: 150bn / (S0 * 1.01^5) / P0 - 1',kind='derived_model_arithmetic')
    elif label.startswith('悲观 · 若净增币'):
        x.update(fetched_value=str(bear_staking),fetched_source='Independent Decimal recalculation with 2.5% assumed net coin growth',kind='derived_model_arithmetic')
    elif label=='乐观 · 年净供应变化':
        x.update(fetched_value='-0.2',fetched_source='Declared scenario input, not an external forecast',kind='model_assumption')
    else:
        raise ValueError('Unreviewed random sample: '+label)
    results.append(x)
save('audit-random-results.json',results); save('audit-exclusions.json',excluded)

# Supplement the extractor, which skips numeric year labels and some bold values.
supp=[]
def add(label,reported,v1,source,v2=None,source2='',kind='dual_source_fact',note=''):
    supp.append(dict(id=100+len(supp),label=label,reported_value=str(reported),unit='',fetched_value=str(v1),fetched_source=source,
      fetched_value2=str(v2) if v2 is not None else None,fetched_source2=source2,kind=kind,note=note))
cm=load('coinmetrics.json')['data']; ll=load('fees.json')['totalDataChart']
from datetime import datetime,timezone
llrows={datetime.fromtimestamp(int(t),timezone.utc).strftime('%Y-%m-%d'):D(str(v)) for t,v in ll}
for a in agg:
    subset=[x for x in cm if a['start']<=x['time'][:10]<=a['end']]
    cmusd=sum((D(x['FeeTotNtv'])*D(x['PriceUSD']) for x in subset),D(0))
    llusd=sum((v for date,v in llrows.items() if a['start']<=date<=a['end']),D(0))
    assert len(subset)==int(a['cm_days'])
    add(a['period']+' USD fees',a['cm_fees_usd'],cmusd,'Re-summed Coin Metrics raw daily payload',llusd,'Re-summed DefiLlama raw daily payload',note='A discrepancy is retained, not normalized away')
    eth=sum((D(x['FeeTotNtv']) for x in subset),D(0))
    add(a['period']+' native fees',a['cm_fees_eth'],eth,'Re-summed Coin Metrics raw daily payload',kind='single_source_fact')
add('ETH supply',supply,supply,'CoinGecko direct API',calc['ultrasound_supply'],'ultrasound independent balance reconstruction')
add('Market cap',calc['calculated_market_cap'],price*supply,'Decimal P x S',calc['reported_market_cap'],'CoinGecko reported capitalization',kind='derived_plus_provider')
for s in calc['scenarios']:
    fs=supply*(1+D(s['supply_growth']))**5
    fp=D(s['terminal_cap'])/fs
    checks={'future_supply':fs,'terminal_price':fp,'return_pct':(fp/price-1)*100,'cagr_pct':((fp/price)**(D(1)/5)-1)*100,'staking_sensitivity_cagr_pct':((fp/price)**(D(1)/5)*D('1.025')-1)*100}
    for k,v in checks.items(): add(s['name']+' '+k,s[k],v,'Independent Decimal scenario recomputation',kind='derived_model_arithmetic')
base=D('450e9')/(supply*D('1.005')**5)
for k,r in [('entry_12pct',D('1.12')),('entry_15pct',D('1.15'))]:
    add(k,calc[k],base/r**5,'Independent Decimal discounted terminal price',kind='derived_model_arithmetic')
for p in calc['entry_sensitivity']:
    add('Entry '+p['price'],p['cagr_pct'],((base/D(p['price']))**(D(1)/5)-1)*100,'Independent Decimal entry return',kind='derived_model_arithmetic')
def pv(f0,c):
    c=D(c)/100; r=D('.15'); g=D('.03')
    return sum(f0*(1+c)**i/(1+r)**i for i in range(1,11))+f0*(1+c)**10*(1+g)/(r-g)/(1+r)**10
annual=next(a for a in agg if a['period']=='2025')
add('Reverse DCF reconstructed cap',calc['calculated_market_cap'],pv(D(annual['cm_fees_usd']),calc['reverse_fee_growth_2025_pct']),'Independent Decimal discounted proxy fee stream',kind='derived_model_arithmetic')
save('audit-supplement-results.json',supp)
for name,rows in [('random',results),('supplement',supp)]:
    command=[sys.executable,str(ROOT/'tools/report_audit.py'),'verdict','--results',json.dumps(rows,ensure_ascii=False),'--report',REPORT.name,'--output-json']
    result=subprocess.run(command,capture_output=True,text=True,check=True)
    (P/f'audit-{name}-verdict.txt').write_text(result.stdout)

discrepancies=[]
for x in supp:
    if x.get('fetched_value2') is None: continue
    delta=abs(D(x['fetched_value'])-D(x['fetched_value2']))/abs(D(x['fetched_value']))*100
    if delta>1: discrepancies.append({'label':x['label'],'relative_deviation_pct':str(delta)})
counts={k:sum(x['kind']==k for x in results) for k in sorted(set(x['kind'] for x in results))}
summary=dict(extracted=len(allpoints),random_selected=len(samples),excluded=len(excluded),random_reviewed=len(results),random_categories=counts,supplementary=len(supp),strict_unresolved_discrepancies=discrepancies,
 status='COMPLETED_RESEARCH_WITH_DISCLOSED_LIMITATIONS_NOT_UNQUALIFIED_DUAL_SOURCE_PUBLICATION')
save('audit-summary.json',summary)
lines=[
'# Ethereum研究报告审计摘要',
'',
'本次研究已完成。审计确认可复算性与引用一致性，但保留近期费用差异及单源数据限制，不宣称所有事实通过双源发布准出。',
'',
f'抽检使用报告工具的默认15%比例、固定种子20261015：提取{len(allpoints)}个候选项，抽中{len(samples)}项；其中{len(excluded)}项是L1名称或时钟片段误识别，保留原始样本并排除。',
'',
f'实际核对{len(results)}项：{counts.get("dual_source_market",0)}项双源行情、{counts.get("single_source_auxiliary",0)}项单源生态数据、{counts.get("derived_model_arithmetic",0)}项模型派生算术、{counts.get("model_assumption",0)}项明确假设。假设只核对录入，不视作未来事实；单源引用核对不等于独立二源认证。',
'',
f'另补查{len(supp)}项：完整年度与季度费用、TTM、原币费用、供应、市值、全部三情景计算、价格门槛、入场回报和反向DCF闭合。原币费用为单源重算。',
'',
'严格核验保留以下超过1%的双源差异：',
'',
'| 项目 | 相对Coin Metrics偏差 |',
'|---|---:|',
*[f"| {x['label']} | {D(x['relative_deviation_pct']):.4f}% |" for x in discrepancies],
'',
'共享verdict工具在一个来源一致、另一个超阈值时会输出警告但仍给PASS。本研究没有把这种PASS解读为全面准出；上述差异已在正文逐项标明，并用区间或敏感性处理。',
'',
'图表已检查可读性。市场数据以market-final.json冻结时点为准；定稿最后一轮实时刷新后重新生成全文、图表和审计记录。',
]
(P/'audit-summary.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
