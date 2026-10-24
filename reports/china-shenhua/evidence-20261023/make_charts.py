"""Static research charts; exact financial values are supplied by verified JSON.

Run with a Python environment containing matplotlib. Floats are used only for
plot geometry, never for valuation or published financial arithmetic.
"""
from pathlib import Path
import json
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
from financial_rigor import exact as D
src=json.loads((HERE/'financials-verified-20261023.json').read_text())
calc=json.loads((HERE/'calculations.json').read_text())
for font in font_manager.fontManager.ttflist:
    if font.name=='Arial Unicode MS':
        plt.rcParams['font.family']=font.name
        break
else:
    plt.rcParams['font.family']='Hiragino Sans'
plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,
 'axes.edgecolor':'#cbd5e1','text.color':'#243746','axes.labelcolor':'#536675',
 'xtick.color':'#536675','ytick.color':'#536675','font.size':11,'axes.unicode_minus':False,
 'savefig.facecolor':'white','figure.facecolor':'white'})

names=['煤炭','发电','铁路','港口','航运','煤化工']
rev=list(map(D,['112375','52363','6947','1249','2651','13753']))
pcts=[v/D('189338')*100 for v in rev]
colors=['#24475c','#527c8b','#7998a4','#9ab0b7','#bccbd0','#b78b62']
fig,axs=plt.subplots(1,2,figsize=(12,4.7),gridspec_kw={'width_ratios':[1.05,1]})
ax=axs[0]
ax.barh(names,[float(v) for v in pcts],color=colors,height=.58)
ax.invert_yaxis(); ax.set_xlim(0,72); ax.set_xlabel('占合并收入（%）')
ax.set_title('外部收入仍以煤、电为主',loc='left',fontsize=14,pad=25)
ax.text(0,1.025,'2026H1｜已抵销内部交易',transform=ax.transAxes,fontsize=10,color='#64748b')
for i,v in enumerate(pcts): ax.text(float(v)+1,i,f'{v:.1f}%',va='center',fontsize=10)
ax=axs[1]
changes=[D(row['pbt_change_yi']) for row in calc['segments_9m']]
ax.barh(names,[float(v) for v in changes],color=['#3c7d7b' if v>=0 else '#a36554' for v in changes],height=.58)
ax.axvline(0,color='#cbd5e1',lw=1); ax.invert_yaxis(); ax.set_xlim(-50,57)
ax.set_xlabel('税前利润同比增减（亿元人民币）')
ax.set_title('煤电的内部抵消值得重视',loc='left',fontsize=14,pad=25)
ax.text(0,1.025,'2026年前三季度｜CAS分部，抵销前',transform=ax.transAxes,fontsize=10,color='#64748b')
for i,v in enumerate(changes): ax.text(float(v)+(1.5 if v>=0 else -1.5),i,f'{v:+.2f}',va='center',ha='left' if v>=0 else 'right',fontsize=10)
fig.subplots_adjust(left=.07,right=.96,top=.83,bottom=.22,wspace=.42)
fig.text(.07,.07,'来源：中国神华2026中报与三季报。两图期间不同；分部利润增减不能直接加总为归母利润增减。',fontsize=9,color='#64748b')
fig.savefig(HERE/'business-economics.png',dpi=180)
plt.close(fig)

annual=src['annual']
years=[str(r['year']) for r in annual]
rows=[]
for r in annual:
    rows.append({**r,'gross_margin_pct':str(D(r['cas_gross_profit'])/D(r['cas_revenue_2025_report_basis'])*100),
       'operating_margin_pct':str(D(r['cas_operating_profit'])/D(r['cas_revenue_2025_report_basis'])*100)})
(HERE/'annual-calculations.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
fig,(ax,ax2)=plt.subplots(1,2,figsize=(12,4.7),gridspec_kw={'width_ratios':[1.5,1]})
series=[('CAS归母利润','cas_parent_profit','#24475c'),('经营现金流','cfo_historical_report_basis','#3c7d7b'),('长期资产现金投入','cash_capex_historical_report_basis','#b78b62')]
for j,(name,key,color) in enumerate(series):
    vals=[D(r[key])/100 for r in annual]
    xs=[i+(j-1)*.24 for i in range(5)]
    ax.bar(xs,[float(v) for v in vals],width=.22,label=name,color=color)
    for x,v in zip(xs,vals): ax.text(x,float(v)+18,f'{v:.0f}',ha='center',fontsize=8)
ax.set_xticks(range(5),years); ax.set_ylim(0,1250); ax.set_ylabel('亿元人民币')
ax.set_title('盈利有周期，现金再投入增加',loc='left',fontsize=14,pad=16)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.11),ncol=3,fontsize=9,frameon=False)
ax.grid(axis='y',alpha=.15); ax.set_axisbelow(True)
for name,key,color in [('毛利率','gross_margin_pct','#24475c'),('营业利润率','operating_margin_pct','#b78b62')]:
    vals=[D(r[key]) for r in rows]
    ax2.plot(years,[float(v) for v in vals],marker='o',lw=2,color=color,label=name)
    for i,v in enumerate(vals): ax2.text(i,float(v)+.7,f'{v:.1f}%',ha='center',fontsize=9)
ax2.set_ylim(17,44); ax2.set_title('五年利润率轮廓',loc='left',fontsize=14,pad=16)
ax2.set_ylabel('%'); ax2.legend(loc='upper center',bbox_to_anchor=(.5,-.11),ncol=2,fontsize=9,frameon=False)
ax2.grid(axis='y',alpha=.15)
fig.subplots_adjust(left=.07,right=.96,top=.85,bottom=.27,wspace=.28)
fig.text(.07,.055,'来源：公司年报。损益按2025年报五年摘要；现金流按各年历史合并边界，不能视作完全可比的内生增长序列。',fontsize=9,color='#64748b')
fig.savefig(HERE/'financial-trend.png',dpi=180)
plt.close(fig)
print(json.dumps(rows,ensure_ascii=False,indent=2))
