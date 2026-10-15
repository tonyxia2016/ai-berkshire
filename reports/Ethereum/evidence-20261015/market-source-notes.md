# Ethereum 市场与链上数据独立取证

研究基准：2026-10-15。先执行 date，实际输出 2026-10-15 13:49:19 CST（Asia/Shanghai）。直接 API/HTML 抓取时间详见 fetch_results*.json；以下 05:xx UTC 对应 13:xx 北京时间。

## 可用于报告的第一实时快照（定稿前应刷新）

|数据提供方|数据内部时间 / 获取时间UTC|价格USD|供应量ETH|市值USD|
|---|---|---:|---:|---:|
|CoinGecko API|last_updated 05:49:51；获取05:50:19.642|2351.84|122136580.3876922|287246123152|
|Coinbase spot|无内部交易时戳；HTTP Date05:50:17，获取05:50:17.217|2350.95|—|—|
|Kraken ticker last c[0]|无内部交易时戳；HTTP Date05:50:13，获取05:50:14.705|2350.50|—|—|
|Coinpaprika|last_updated05:49:18；获取05:50:12.629|2352.5360106414246|**total_supply旧字段不采用**|287330702666|

主快照建议采用 CoinGecko 的同一 JSON 内价格/供应/市值，另用 Coinbase/Kraken 独立成交所核验价格。它们是同一分钟附近快照，并非精确同一秒成交。CoinGecko × 供应计算市值与披露值偏差接近0；financial_rigor_checks.txt已保存CLI检查。

Coinpaprika total_supply=120232214 与其市值/价格隐含的约122.137M矛盾，不能用于供应。其价格仍有独立价值。不要把staked ETH从市场流通供应机械扣掉：LST仍可交易、质押可退出、供应定义本来包含质押。CMC网页和CG网页本次web工具约$2360-$2363，但没有内部时间，不作为API快照的同刻来源；搜索片段$2419是凌晨旧快照，更不采用。

供应独立核验：Etherscan直接HTML显示122131842.40 ETH，获取05:50:14.181 UTC；ultrasound供给分项（block26195923 / slot15434942）算得122130235.290364856728955334 ETH；CG122136580.3876922。极小差异应保留采集与口径差别，不强行要求相同。Ultrasound `supply=executionBalancesSum/1e18+(beaconBalancesSum-beaconDepositsSum)/1e9`，不可将beacon字段错误按wei处理。

API链接：
- [CoinGecko完整行情](https://api.coingecko.com/api/v3/coins/ethereum?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false)
- [Coinbase现货](https://api.coinbase.com/v2/prices/ETH-USD/spot)
- [Kraken现货](https://api.kraken.com/0/public/Ticker?pair=ETHUSD)
- [Coinpaprika行情](https://api.coinpaprika.com/v1/tickers/eth-ethereum)
- [Etherscan供应](https://etherscan.io/stat/supply)
- [ultrasound.money](https://ultrasound.money/)

## 网络收费：五完整年、四完整季和TTM

美元单位是**百万美元**。CM按每日 FeeTotNtv × PriceUSD 再求和；日末价换算，不是逐笔实现美元收入。Llama为提供商dailyFees美元总额。年度2021—2025记录完整365/366日，TTM=2025-10-15—2026-10-14完整365日；不包含10月15日未完成日。脚本aggregate.py可复算。

|期间|CM ETH费用|CM美元费用百万|Llama美元费用百万|Llama相对CM偏差|CM净供应变化ETH|
|---|---:|---:|---:|---:|---:|
|2021|3,446,698.30|9,919.925071|9,909.658913|-0.103%|未取2020年末基点|
|2022|1,766,038.69|4,300.010048|4,303.921493|+0.091%|+2,487,166.88|
|2023|1,309,054.54|2,406.636018|2,406.927533|+0.012%|-342,056.55|
|2024|793,879.31|2,473.101586|2,470.611881|-0.101%|+285,258.52|
|2025|171,840.80|520.714382|523.172315|+0.472%|+865,065.99|
|2025Q4|21,505.80|76.671974|76.091098|-0.758%|+236,400.87|
|2026Q1|17,425.08|39.951070|39.727936|-0.559%|+241,474.82|
|2026Q2|24,834.74|52.472425|51.782628|-1.315%|+248,103.63|
|2026Q3|15,695.98|35.403107|34.601936|-2.263%|+263,627.88|
|TTM|75,382.39|183.720934|181.717450|-1.091%|+996,892.10|

**差异未完全调平，不应强凑通过**：2026Q2两者偏差1.315%，Q3 2.263%，TTM1.091%。官方定义两者都包括execution base fee + priority fee + blob fee，所以不是简单漏blob。Llama源码每个窗口toBlock减50块并用自身币价换算；CM日结价格不同可能贡献差异，但现有证据不能把全部偏差精确归因。TTM建议报告区间$181.7m—$183.7m，2025全年$520.7m—$523.2m。按项目工具的“偏离中位数”算法，偏差是两源差值的一半附近，不能用工具通过掩盖pairwise差异。

[Coin Metrics原始API](https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=eth&metrics=FeeTotNtv,PriceUSD,SplyCur&frequency=1d&start_time=2021-01-01&end_time=2026-10-15&page_size=10000)；[DeFiLlama费用API](https://api.llama.fi/summary/fees/ethereum?dataType=dailyFees)；[CM收费口径](https://gitbook-docs.coinmetrics.io/network-data/network-data-overview/fees-and-revenue/fees)；[Llama源码](https://github.com/DefiLlama/dimension-adapters/blob/master/fees/ethereum/index.ts)。源码原文也已留存llama_adapter.txt。

**不能称公司营收或FCF**：这些是网络使用者支付协议费用；base/blob被销毁，priority给区块提议者；协议外MEV转账另计。持有ETH并不拥有运营公司的法定权益，费用/市值只能作网络定价压力测试，不能直接称P/E或P/FCF。

## 销毁、发行和质押

Ultrasound原始Next.js JSON（本地ultrasound_nextdata.json）`gauge-rates d30`更新时间2026-10-15 05:48:11 UTC，近30日速度年化：发行1082514.202288312 ETH，销毁30284.58915454633 ETH，净供应增长年化0.8615635682941965%。这只是最近30日折年，非一年预测；不是固定收益。`burn-sums d30`实际销毁2487.440587642409 ETH，美元6554815.422196462（各期汇率），累计自EIP1559销毁4640965.634201828 ETH。最近一天只有49.1135 ETH销毁，不能将这种单日低点永久外推。

Llama dailyRevenue的TTM销毁估计$50.396m，近30日$6.499m；与Ultrasound近30日$6.555m方向一致、窗口略有差。**Llama当前源码用每块min(effective_gas_price)近似base fee**，存在把最小priority fee误作burn的可能，因此该销毁统计只能作为近似指标。CM SplyBurntNtv/IssTotNtv社区端点403，未获得完整双源年度发行/销毁序列，不伪造。年度净供应变化来自CM SplyCur端点差，不能替代 gross issuance 和 gross burn 的分解。

[ValidatorQueue](https://www.validatorqueue.com/)注明数据来自Beaconcha.in，本次直接HTML内部lastUpdated=2026-10-15 03:44:23.051544 UTC，抓取05:52:12.363 UTC。835919名active validators；staked43,673,126 ETH /35.77%；7d APR2.58%；入场队列1,282,776 ETH /22.27日；退出978,751 ETH /16.99日另加sweep7.3日。Ultrasoundscarcity粗核staked43,756,079 ETH（不同块、约6小时前指标），两者差0.19%上下，不能称同秒精确对齐。APR是ETH本位网络显示的毛指标，不是美元保证收益；运营、服务费和惩罚风险需要另扣。

|期末|质押ETH|显示APR|质押占比|
|---|---:|---:|---:|
|2023-12-31|28,704,479|3.62%|23.88%|
|2024-12-31|33,729,980|3.03%|28.0%|
|2025-12-31|35,567,591|2.85%|29.31%|
|2026-03-31|38,435,676|2.76%|31.62%|
|2026-06-30|40,068,501|2.71%|32.89%|
|2026-09-30|43,663,442|2.63%|35.77%|
|2026-10-15|43,673,126|2.58%|35.77%|

上述质押历史为ValidatorQueue/Beaconcha.in单条采集链，尚无第二独立年末全序列核验；2023—2025增长与毛收益下行可作趋势证据，不列最高置信级。Validator数量下降不能等同安全资本流失：Pectra后允许合并有效余额，质押ETH数量应同时观察。

## 年末价格交叉核验

|年末UTC|CM参考价|Coinbase日K收盘USD|差异说明|
|---|---:|---:|---|
|2021-12-31|3686.9518|3675.80|参考复合价与单交易所收盘，非完全相同口径|
|2022-12-31|1195.3309|1195.25|参考复合价与单交易所收盘，非完全相同口径|
|2023-12-31|2279.0757|2281.07|参考复合价与单交易所收盘，非完全相同口径|
|2024-12-31|3332.4548|3330.32|参考复合价与单交易所收盘，非完全相同口径|
|2025-12-31|2968.1280|2966.84|参考复合价与单交易所收盘，非完全相同口径|

Coinbase按UTC日K取candle[4]收盘，原始响应和时间/URL在coinbase_yearend_*.json及coinbase_yearends.json；[官方candle字段定义](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles)。

## 文件目录

全部原始API/HTML、提取序列、再现脚本位于`/tmp/eth_market_20261015/`；请主代理按需要复制至本次研究证据目录，不改旧报告。低可信或未独立核验项已明示。没有使用旧报告数值作为来源。
