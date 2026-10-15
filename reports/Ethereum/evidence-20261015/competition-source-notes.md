# Ethereum 护城河、竞争、治理与监管证据摘要

研究基线：2026-10-15（date 输出 Thu Oct 15 13:49:05 CST 2026）；以下是供主报告整合的研究材料，不是独立发布报告。行情以主代理双源为准。

## 可以直接采用的核心判断

以太坊的护城河主要在可组合的资本与抵押品、成熟开发工具、可被不同参与者共同验证的结算规则，以及机构迁移所需的运营与安全积累。开源代码可以复制，深流动性和各方共同承认的结算历史不能瞬间复制。但 ETH 不是这些应用收入的股权；链上资产规模与 ETH 持有者收益之间，必须经过费用燃烧、验证服务收入以及 ETH 作为抵押/储备资产的需求三个渠道，不能跳过价值捕获环节。

L2 同时是分销渠道和议价强的客户。EF 2026-03-23 已调整叙事：L1 承担结算、共享状态与流动性枢纽，L2 首要角色转向功能差异、定制和触达用户；官方也承认 L1–L2 的某些利益联系仍需测量验证。因此不应把 L2 交易量增长直接视为 ETH 盈利增长。推断：扩容产生消费者剩余，只有需求增长、结算费和抵押品需求足够强，ETH 才能拿到其中一部分。

来源：[EF L1/L2 关系说明，2026-03-23](https://blog.ethereum.org/2026/03/23/l1-l2-ethereum)。该页衍生摘要宜控制在200英文词等量以内。

## 竞争辅助数据（单一 provider，不参与估值）

直接请求 DefiLlama API，HTTP Date 为 2026-10-15 05:50:48 UTC：

| 网络 | DeFi TVL（美元） |
|---|---:|
| Ethereum | 49,341,166,839.62088 |
| Solana | 5,925,009,384.418988 |
| Base | 6,042,938,489.996456 |
| Arbitrum | 1,357,876,858.6506436 |
| Tron | 5,487,469,954.269532 |

[DefiLlama chains API](https://api.llama.fi/v2/chains)

有明确底层日期的历史序列：Ethereum 2026-10-15 00:00 UTC，TVL 49,248,843,909 美元；2026-10-14 00:00 UTC，50,917,908,224 美元。它与上表实时聚合不同时间，不应混写。[历史 API](https://api.llama.fi/v2/historicalChainTvl/Ethereum)

稳定币 API，HTTP Date 为 2026-10-15 05:50:54 UTC，以下**仅 peggedUSD**，不是所有货币稳定币总和：Ethereum 143,956,531,938.1858 美元；Solana 15,731,165,441.226084；Tron 94,571,891,685.12424；Base 5,171,143,023.431851；Arbitrum 3,667,015,353.8947215。[API](https://stablecoins.llama.fi/stablecoinchains)

这些是单一数据商实时采集值；HTTP Date 不等于底层链的精确区块时间。主报告可用约数并注明单源辅助。Ethereum L1 TVL 不能直接与 L2 TVS 相加，避免桥接与再抵押重复。

网页观察补充（采集10/15，页面没有精确样本时间，不建议主表使用）：Ethereum 24h DEX $1.256b、Solana $2.084b；前者资本存量更大，并不意味着所有交易业务领先。单日交易量易受价格与投机活动影响，不能拿来作为持续盈利能力。[Ethereum](https://defillama.com/chain/ethereum)，[Solana](https://defillama.com/chain/solana)。

RWA：DefiLlama Ethereum 页抓到 Active AUM $14.102b，Solana $2.405b，页面无精确样本时间，且 RWA.xyz 正式域名页超出抓取长度；搜索出现近似域名 app.rwa-xyz.com，未使用。建议不引用未独立核实的 RWA 排名/份额，作为缺口。不能把 tokenized AUM 当交易量、ETH 市值支撑或收入。

开发者：Electric Capital 官网当前明确把年度报告列为2018–2024，并转向 Open Dev Data。动态 ETH/SOL 页未显示可靠2026人数；不可把二手“2025 Solana 总开发者第一”等断言写入报告。官网2024综合结果显示跨链开发已普遍，约三分之一开发者跨链，说明人力护城河并非独占；这是2024历史背景，非2026现状。[Electric Capital Analysis](https://www.developerreport.com/developer-report)。2026全职、资深开发者留存及可比跨链数据缺口应明示。

## 治理：用制衡和交付能力替代 CEO 评分

ETH 持有者并不拥有 EF、核心开发团队或协议应用的剩余索取权。Ethereum 核心治理为链下协调：EIP 作者提案，客户端开发者实现，验证者和节点选择升级，应用、用户及资产发行方决定使用哪条规范链。EF 负责资助、协调和方向倡议，不等于能单方面对协议下令的上市公司管理层。[Ethereum governance](https://ethereum.org/governance/)

EF 2026-02-13 董事会公告：Tomasz Stańczak 离开 Co-ED，Bastian Aue 成为 interim Co-ED，结合其本人公告继续与 Hsiao-Wei 协作。2026-06-23 EF 重组削减54人、约20%，工作分为五个业务领域外加运营和管理。不能只把裁员认定为成本纪律，也不能当成技术衰败；应看客户端多样性、安全事件、路线交付、资助续航与关键人才接续。[领导交接](https://blog.ethereum.org/2026/02/13/leadership-update)，[重组](https://blog.ethereum.org/2026/06/23/ef-structure)

重要利益边界：EF 宗旨强调抗审查、开源、隐私和安全；用户低成本与去中心化可能优先于 ETH 持有者短期收益。对此应给予清楚定位，不能套“优秀管理层会最大化股东回报”。[2026-03-13 Mandate](https://ethereum.org/foundation/mandate)

## 升级和 L2 安全事实

- 2026-09-28 EF 公告明确 Glamsterdam 的 Sepolia 激活计划为10/6；Hoodi/mainnet仍TBD。ethereum.org写Q4 2026 expected、date unconfirmed，不是主网已上线证明。公告涵盖 ePBS、block-level access lists 与 gas repricing。升级提高可用容量是事实方向；何时交付及是否增厚 ETH 经济收益均不确定。[官方测试网公告](https://blog.ethereum.org/en/2026/09/17/glamsterdam-testnet-announcement)，[官方升级页](https://ethereum.org/roadmap/glamsterdam/)
- Hegotá 后续升级的 FOCIL 已作为共识层主项，账户抽象具体方案仍需共识（2026-04-10报告）。不应将未来功能列作已经具备。[Checkpoint #9](https://blog.ethereum.org/2026/04/10/checkpoint-9)
- L2Beat 采集时 Base 与 Arbitrum One 均 Stage 1，仍有安全委员会/升级退出窗口方面限制，不能宣称全部继承 L1 完整安全。阶段衡量去信任进展，本身不等于安全评级。[L2Beat](https://l2beat.com/layer2s/summary)。页面顶部$0.00属于加载占位值，不得引用。

## 美国监管：2026年应更新，范围必须保留

SEC 于2026-03-17发布、3/23生效的解释性文件明确将 Ether (ETH) 列为 digital commodity 示例，并认为此类别资产本身不是证券。文件仍区分代币本身和附带投资合同的交易；解释不取代 Howey。它讨论符合列明条件的 protocol staking 与 staking receipts，**明确没有覆盖 restaking**（PDF第40页脚注107）；保证/自行设定奖励，或提供方自主决定是否、何时、质押多少等结构也可能在所述范围之外（第50页脚注124–126）。因此可说美国本体分类及标准质押路径更清晰，不可说所有ETH投资、所有LST及再质押均无证券监管风险。

[SEC release入口](https://www.sec.gov/rules-regulations/2026/03/s7-2026-09)，[正式PDF](https://www.sec.gov/files/rules/interp/2026/33-11412.pdf)，[SEC简明分类页](https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/crypto-assets-federal-securities-laws)

9/28更新FAQ补充 receipt 的条件：不改变标的权利、不让发方借贷/质押/再质押标的，且FAQ明确只是工作人员意见、没有法律效力。[最新FAQ](https://www.sec.gov/about/divisions-offices/division-corporation-finance/faqs-crypto-assets)。法规/解释/工作人员意见三个层级不要混用。

## 最强多空对抗与可证伪点（以下为研究推断）

多方最强版本：机构与应用愿意为可信中立、公开可验证的共同结算层付费；L1集中价值、L2扩大应用边界，ETH既担保网络安全又作通用抵押品，长期货币需求可能比当前gas现金流大。论据是资本存量与可组合基础，不是单纯TPS领先。

空方最强版本：以太坊成功不自动等于ETH高回报。稳定币用户要的是美元，RWA投资者要的是利息，L2运营方保留排序收入；扩容使一笔交易消耗的ETH费用更少，即时换币还能减少持币余额。若大量价值停留在应用、稳定币发行商和排序器，ETH市值主要依赖货币溢价，利润法无法给它稳固下限。

反直觉但重要：廉价gas不自动是坏事；它也许扩大需求。真正应否证的是“总生态使用上升会在合理时限内创造足够外部ETH需求/燃烧”，而非要求每笔交易越来越贵。

可观测指标与审查触发（主观研究规则，非已发生事实）：
1. 连续两个季度：L1/L2用户或稳定币存量扩大，但90日总燃烧与L2向L1实际付费继续下降，且ETH抵押品份额未提高——重审价值捕获，不可用TPS叙事搪塞。
2. 稳定币/RWA净发行和TVL份额在同口径下连续两个季度流失，同时资深开发者留存下滑——护城河重审；价格下跌造成美元TVL下降必须单独剥离。
3. 重大finality故障、相关性罚没、长期审查，或主要L2退出机制不能执行——立即重审安全溢价，不等季度。
4. Glamsterdam再次实质延期、客户端集中度上升或核心资助断层——评估治理执行能力；不要把某位名人离职本身当卖出信号。
5. 法律变化限制持有、赎回或可用通道——按产品和所在地重审，不能仅靠美国ETF/SEC结论外推全世界。
