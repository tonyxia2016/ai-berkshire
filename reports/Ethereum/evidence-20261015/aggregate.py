"""Reproduce exact Decimal ETH fee aggregates from saved Coin Metrics/DefiLlama payloads."""
import json, datetime, pathlib
from decimal import Decimal as D
P = pathlib.Path(__file__).resolve().parent
cm = json.loads((P/'coinmetrics.json').read_text())['data']
def dated(name):
    return {datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y-%m-%d'):D(str(v)) for t,v in json.loads((P/name).read_text())['totalDataChart']}
ll, burn = dated('fees.json'), dated('revenue.json')
periods=[(str(y),f'{y}-01-01',f'{y}-12-31') for y in range(2021,2026)]+[('2025Q4','2025-10-01','2025-12-31'),('2026Q1','2026-01-01','2026-03-31'),('2026Q2','2026-04-01','2026-06-30'),('2026Q3','2026-07-01','2026-09-30'),('TTM','2025-10-15','2026-10-14')]
rows=[]
for name,start,end in periods:
    r=[x for x in cm if start<=x['time'][:10]<=end]
    f=sum((D(x['FeeTotNtv'])*D(x['PriceUSD']) for x in r),D(0))
    n=sum((D(x['FeeTotNtv']) for x in r),D(0))
    l=[v for d,v in ll.items() if start<=d<=end]; lf=sum(l,D(0))
    row=dict(period=name,start=start,end=end,cm_days=len(r),llama_days=len(l),cm_fees_eth=str(n),cm_fees_usd=str(f),llama_fees_usd=str(lf),fee_deviation_percent=str((lf/f-1)*100),llama_burn_usd=str(sum((v for d,v in burn.items() if start<=d<=end),D(0))),cm_end_price=r[-1]['PriceUSD'],cm_end_supply=r[-1]['SplyCur'])
    prev=(datetime.date.fromisoformat(start)-datetime.timedelta(days=1)).isoformat()
    rp=[x for x in cm if x['time'][:10]==prev]
    if rp:
        row['cm_start_supply']=rp[0]['SplyCur']
        row['cm_net_supply_change_eth']=str(D(row['cm_end_supply'])-D(rp[0]['SplyCur']))
    rows.append(row)
(P/'aggregates.json').write_text(json.dumps(rows,indent=2))
