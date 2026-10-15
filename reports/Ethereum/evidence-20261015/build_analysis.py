"""Reproduce this report's inputs, Decimal scenarios, and local figures.

Run --refresh for a new directly fetched market snapshot; ordinary runs reuse it.
The report template uses frozen observations. Monetary terminal values are assumptions.
"""
from pathlib import Path
from decimal import Decimal as D, getcontext
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import concurrent.futures, contextlib, importlib.util, io, json, sys, urllib.request

getcontext().prec = 40
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def read(name):
    return json.loads((HERE/name).read_text(), parse_float=str)
def save(name, obj):
    (HERE/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str)+'\n')
def f(v, n=2): return f'{D(v):,.{n}f}'
def pct(v): return f'{D(v):+.2f}%'
def dev(a,b): return abs(D(a)-D(b))/D(a)*100

urls = {
 'coingecko':'https://api.coingecko.com/api/v3/coins/ethereum?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false',
 'coinbase':'https://api.coinbase.com/v2/prices/ETH-USD/spot',
 'kraken':'https://api.kraken.com/0/public/Ticker?pair=ETHUSD',
}
if '--refresh' in sys.argv:
    def fetch(item):
        name,url=item
        req=urllib.request.Request(url,headers={'User-Agent':'EthereumResearch/1.0','Cache-Control':'no-cache'})
        with urllib.request.urlopen(req,timeout=35) as resp:
            data=json.loads(resp.read().decode(),parse_float=str)
            return name,dict(url=url,retrieved_utc=datetime.now(timezone.utc).isoformat(),http_date=resp.headers.get('Date'),data=data)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        snap=dict(pool.map(fetch,urls.items()))
    save('market-final.json',snap)
elif (HERE/'market-final.json').exists():
    snap=read('market-final.json')
else:
    metadata={x['source']:x for x in read('fetch_results.json')}
    snap={name:dict(url=urls[name],retrieved_utc=metadata[name]['retrieved_utc'],http_date=metadata[name]['http_date'],data=read(name+'.json')) for name in urls}
    save('market-final.json',snap)

cg=snap['coingecko']['data']; md=cg['market_data']
price=D(md['current_price']['usd']); supply=D(md['circulating_supply']); cap=price*supply
cb=D(snap['coinbase']['data']['data']['amount'])
kr=D(next(iter(snap['kraken']['data']['result'].values()))['c'][0])
source_time=cg.get('last_updated',md.get('last_updated'))
local=datetime.fromisoformat(source_time.replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Shanghai'))
fetch_local=datetime.fromisoformat(snap['coingecko']['retrieved_utc']).astimezone(ZoneInfo('Asia/Shanghai'))
assert local.date().isoformat()=='2026-10-15', 'Not a current-day market observation'
assert (fetch_local-local).total_seconds()<900, 'Market observation is over 15 minutes stale'
assert max(dev(price,cb),dev(price,kr))<1, 'Price sources differ by over 1%'
u=read('ultrasound.json'); parts=u[0]['data']
usupply=D(parts['executionBalancesSum'])/D(10)**18+(D(parts['beaconBalancesSum'])-D(parts['beaconDepositsSum']))/D(10)**9
effective=D(u[3]['data']['sum'])/D(10)**9
growth=D(u[2]['data']['d30']['supply_growth_rate_yearly'])*100
aggregates=read('aggregates.json')
years={x['period']:x for x in aggregates}
ttm=years['TTM']; annual=D(years['2025']['cm_fees_usd'])
ttm_low=min(D(ttm['cm_fees_usd']),D(ttm['llama_fees_usd']))
ttm_high=max(D(ttm['cm_fees_usd']),D(ttm['llama_fees_usd']))
out={'price':price,'supply':supply,'calculated_market_cap':cap,'reported_market_cap':D(md['market_cap']['usd']),
 'coinbase':cb,'kraken':kr,'price_deviation_cb_pct':dev(price,cb),'price_deviation_kr_pct':dev(price,kr),
 'ultrasound_supply':usupply,'supply_deviation_pct':dev(supply,usupply),'effective_stake':effective,
 'effective_stake_share_pct':effective/usupply*100,'net_supply_growth_30d_annualized_pct':growth,
 'source_time_utc':source_time,'source_time_beijing':local.isoformat(),'fetch_time_beijing':fetch_local.isoformat(),
 'annual_fee_multiple':cap/annual,'ttm_fee_multiple_low':cap/ttm_high,'ttm_fee_multiple_high':cap/ttm_low,
 'annual_fee_yield_pct':annual/cap*100,
 'annual_usd_fee_change_2025_pct':(annual/D(years['2024']['cm_fees_usd'])-1)*100,
 'annual_eth_fee_change_2025_pct':(D(years['2025']['cm_fees_eth'])/D(years['2024']['cm_fees_eth'])-1)*100,
 'q3_q2_eth_fee_change_pct':(D(years['2026Q3']['cm_fees_eth'])/D(years['2026Q2']['cm_fees_eth'])-1)*100}

# A gross-fee proxy DCF, explicitly not ETH owner FCF or intrinsic value.
r=D('.15'); g=D('.03')
def fee_pv(f0,step):
    values=[f0*(1+step)**n/(1+r)**n for n in range(1,11)]
    return sum(values)+f0*(1+step)**10*(1+g)/(r-g)/(1+r)**10
def solve_rate(f0):
    lo,hi=D('0'),D('2')
    for _ in range(150):
        mid=(lo+hi)/2
        if fee_pv(f0,mid)<cap: lo=mid
        else: hi=mid
    return (lo+hi)/2
out.update(reverse_fee_growth_2025_pct=solve_rate(annual)*100, reverse_fee_growth_ttm_low_pct=solve_rate(ttm_high)*100,reverse_fee_growth_ttm_high_pct=solve_rate(ttm_low)*100)
growth10=out['reverse_fee_growth_2025_pct']/100
out['reverse_fee_year10']=annual*(1+growth10)**10
out['reverse_terminal_pv_share_pct']=out['reverse_fee_year10']*(1+g)/(r-g)/(1+r)**10/cap*100
scenarios=[]
for name,target,netgrowth in [('悲观','150000000000','.01'),('中性','450000000000','.005'),('乐观','900000000000','-.002')]:
    future_supply=supply*(1+D(netgrowth))**5
    terminal_price=D(target)/future_supply
    cagr=(terminal_price/price)**(D(1)/5)-1
    scenarios.append(dict(name=name,terminal_cap=D(target),supply_growth=D(netgrowth),future_supply=future_supply,terminal_price=terminal_price,
      return_pct=(terminal_price/price-1)*100,cagr_pct=cagr*100,staking_sensitivity_cagr_pct=((1+cagr)*D('1.025')-1)*100))
out['scenarios']=scenarios
base=scenarios[1]['terminal_price']
out['entry_15pct']=base/D('1.15')**5; out['entry_12pct']=base/D('1.12')**5
out['entry_sensitivity']=[dict(price=D(p),cagr_pct=((base/D(p))**(D(1)/5)-1)*100) for p in ['1500','1800','2000',str(price),'3000','4000']]
out['required_terminal_cap_12pct']=price*D('1.12')**5*scenarios[1]['future_supply']
out['required_terminal_cap_15pct']=price*D('1.15')**5*scenarios[1]['future_supply']
out['staking_downside_example_pct']=(D('1.025')*D('.7')-1)*100
save('calculations.json',out)

spec=importlib.util.spec_from_file_location('rigor',ROOT/'tools/financial_rigor.py')
rigor=importlib.util.module_from_spec(spec); spec.loader.exec_module(rigor)
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    rigor.verify_market_cap(str(price),str(supply),str(md['market_cap']['usd']),'USD')
    rigor.cross_validate('ETH price',{'CoinGecko':price,'Coinbase':cb,'Kraken':kr},'USD',1)
    rigor.cross_validate('ETH supply',{'CoinGecko':supply,'ultrasound':usupply},'ETH',1)
    for a in aggregates:
        rigor.cross_validate(a['period']+' L1 total fees',{'CoinMetrics':a['cm_fees_usd'],'DefiLlama':a['llama_fees_usd']},'USD',1)
        print('PAIRWISE relative to CoinMetrics:',dev(a['cm_fees_usd'],a['llama_fees_usd']),'%')
    for s in scenarios:
        rigor.exact_calc(f"{s['terminal_cap']} / ({supply} * (1 + ({s['supply_growth']})) ** 5)")
        print('AUTHORITATIVE Decimal:',s)
    print('Decimal complete results:',json.dumps(out,ensure_ascii=False,default=str))
(HERE/'financial-rigor.txt').write_text(buf.getvalue())

tokens={
 'PRICE':f(price),'SUPPLY':f(supply,4),'CAP':f(cap/D('1e8')),'REPORTED_CAP':f(D(md['market_cap']['usd'])/D('1e8')),
 'CAP_DEV':f(dev(cap,md['market_cap']['usd']),3),'TOOL_MARKET_OUTPUT':'\n'.join(buf.getvalue().splitlines()[:11]),
 'CB':f(cb),'KR':f(kr),'CB_DEV':f(dev(price,cb),3),'KR_DEV':f(dev(price,kr),3),
 'QUOTE_TIME':local.strftime('%H:%M:%S'),'FETCH_TIME':fetch_local.strftime('%H:%M:%S'),
 'USUPPLY':f(usupply,4),'SUPPLY_DEV':f(dev(supply,usupply),4),'STAKE_SHARE':f(effective/usupply*100),
 'FEE_MULT':f(cap/annual,0),'TTM_MULT_LOW':f(cap/ttm_high,0),'TTM_MULT_HIGH':f(cap/ttm_low,0),
 'FEE_YIELD':f(annual/cap*100,3),'USD_DROP':pct(out['annual_usd_fee_change_2025_pct']),'ETH_DROP':pct(out['annual_eth_fee_change_2025_pct']),
 'Q3_ETH_DROP':pct(out['q3_q2_eth_fee_change_pct']),'REVERSE_ANNUAL':f(out['reverse_fee_growth_2025_pct'],1),
 'REVERSE_YEAR10':f(out['reverse_fee_year10']/D('1e8'),0),'REVERSE_TV_SHARE':f(out['reverse_terminal_pv_share_pct'],1),
 'REVERSE_TTM_LOW':f(out['reverse_fee_growth_ttm_low_pct'],1),'REVERSE_TTM_HIGH':f(out['reverse_fee_growth_ttm_high_pct'],1),
 'ENTRY_15':f(out['entry_15pct'],0),'ENTRY_12':f(out['entry_12pct'],0),'BASE_RETURN':pct(scenarios[1]['cagr_pct']),
 'REQUIRED_CAP_12':f(out['required_terminal_cap_12pct']/D('1e8'),0),'REQUIRED_CAP_15':f(out['required_terminal_cap_15pct']/D('1e8'),0),
 'SCENARIO_ROWS':'\n'.join('| '+ ' | '.join([s['name'],f(s['terminal_cap']/D('1e8'),0),pct(s['supply_growth']*100),f(s['future_supply']/D('1e6'),3),f(s['terminal_price'],0),pct(s['return_pct']),pct(s['cagr_pct']),pct(s['staking_sensitivity_cagr_pct'])])+' |' for s in scenarios),
 'ENTRY_ROWS':'\n'.join(f"| {f(x['price'])} | {pct(x['cagr_pct'])} |" for x in out['entry_sensitivity']),
 'ANNUAL_ROWS':'\n'.join('| '+ ' | '.join([a['period']+'年',f(D(a['cm_fees_usd'])/D('1e8')),f(D(a['cm_fees_eth'])/D('1e4')),f(dev(a['cm_fees_usd'],a['llama_fees_usd']))+'%'])+' |' for a in aggregates if a['period'] in [str(y) for y in range(2021,2026)]),
 'QUARTER_ROWS':'\n'.join('| '+ ' | '.join([a['period'],f(D(a['cm_fees_usd'])/D('1e6')),f(D(a['llama_fees_usd'])/D('1e6')),f(D(a['cm_fees_eth'])),f(dev(a['cm_fees_usd'],a['llama_fees_usd']))+'%', '通过' if dev(a['cm_fees_usd'],a['llama_fees_usd'])<=1 else '超阈值，保留差异'])+' |' for a in aggregates if 'Q' in a['period']),
}
save('render_tokens.json',tokens)
template=HERE/'report-template.md'
if template.exists():
    text=template.read_text()
    for k,v in tokens.items(): text=text.replace('{{'+k+'}}',v)
    (HERE.parent/'Ethereum研究报告-20261015.md').write_text(text)

sys.path.insert(0,'/tmp/eth-research-plot-deps')
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#fbfaf7','axes.facecolor':'#fbfaf7'})
    fig,axs=plt.subplots(1,2,figsize=(11.5,4.3))
    ay=[years[str(y)] for y in range(2021,2026)]
    for ax,field,div,title in [(axs[0],'cm_fees_usd',1e9,'Total L1 fees (USD bn)'),(axs[1],'cm_fees_eth',1e6,'Total L1 fees (million ETH)')]:
        vals=[float(a[field])/div for a in ay]
        ax.bar([a['period'] for a in ay],vals,color=['#b4c8d5']*4+['#235b78'],width=.65)
        ax.set_title(title,loc='left',pad=15)
        ax.set_ylim(0,max(vals)*1.2)
        for i,v in enumerate(vals): ax.text(i,v+max(vals)*.025,f'{v:.2f}',ha='center',fontsize=10)
    fig.suptitle('Ethereum: lower fees in both dollars and native units',x=.06,ha='left',fontsize=15)
    fig.text(.06,.015,'Source: Coin Metrics daily series; full-year USD totals checked against DefiLlama. Not holder earnings.',fontsize=9,color='#555555')
    fig.tight_layout(rect=(.02,.05,.99,.92)); fig.savefig(HERE/'annual-fees.png',dpi=170); plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4.7))
    xs=list(range(1200,4201,20)); ys=[(float(base)/x)**.2*100-100 for x in xs]
    ax.plot(xs,ys,color='#235b78',lw=2.5)
    ax.axhspan(12,15,color='#e7ebde',label='Assumed required return: 12–15%')
    ax.axvline(float(price),color='#af5d46',linestyle='--',label=f'Live snapshot: ${float(price):,.2f}')
    ax.scatter([float(price)],[float(scenarios[1]['cagr_pct'])],color='#af5d46',zorder=3)
    ax.set_xlabel('Entry price (USD / ETH)'); ax.set_ylabel('Five-year price CAGR (%)')
    ax.set_title('Entry price matters — even if the network succeeds',loc='left',pad=16,fontsize=15)
    ax.legend(frameon=False); ax.grid(axis='y',alpha=.18)
    fig.text(.085,.015,'Assumptions: terminal market cap $450bn; annual supply growth +0.5%; no staking, tax or fees. Not a forecast.',fontsize=9,color='#555555')
    fig.tight_layout(rect=(.02,.05,.99,.98)); fig.savefig(HERE/'entry-returns.png',dpi=170); plt.close(fig)
except ImportError:
    print('Optional figures require matplotlib; calculations and report completed.')
print(json.dumps({'price':str(price),'beijing_time':local.isoformat(),'base_cagr':str(scenarios[1]['cagr_pct']),'entry_range':[str(out['entry_15pct']),str(out['entry_12pct'])]},ensure_ascii=False))
