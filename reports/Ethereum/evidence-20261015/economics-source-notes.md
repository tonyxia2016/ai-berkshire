# Ethereum 协议经济与价值捕获研究便笺

研究执行时间：`date` 为 2026-10-15 13:48:58 CST（Asia/Shanghai）。资料查询截至 2026-10-15。只读研究，未修改已有报告。

## 核心判断

Ethereum 网络使用增长与 ETH 投资回报之间有两道需要实证的传导：用户活动是否变成 Ethereum L1/Blob 的付费稀缺资源需求；资源收入是否通过销毁、给验证者的费用及货币/抵押品需求，足以抵消新增发行与竞争性成本下降。ETH 不是 Ethereum Foundation 的股权，网络收入不是可向所有持有人分红的企业净利润。质押收入里很大部分是新发行，不能不加区分当外部客户现金流。

## 12 条重要事实与反证

1. **EIP-1559 销毁的是 L1 base fee，priority fee 给区块生产方。** base fee 随区块使用量相对目标调整，不是固定佣金率。持币者受益于供给减少，但不会收到一笔现金分红；不能把全部 gas fee 当持币者收入。机制事实高置信；EIP created 2019-04-13，London 2021-08 上线，截至查询仍有效。来源 https://eips.ethereum.org/EIPS/eip-1559 。

2. **ETH 没有承诺永远通缩。** Merge 后执行层新增发行归零，共识层仍发行奖励。净供应变化取决于发行减销毁。总有效质押增加会提高总发行，而降低单位质押本金的基础收益率（近似平方根关系）。机制高置信，文档更新2026-09-28。来源 https://ethereum.org/developers/docs/consensus-mechanisms/pos/rewards-and-penalties/ 。

3. **质押收益要拆分发行、tips、MEV，并扣服务费/运维/罚没风险。** MEV不是协议凭空创造的现金，搜索者、构建者、验证者分享价值；仅持有未质押 ETH 不会自动收到这些收入。发行为全体持有人承担稀释的安全预算，不能和外部付费等同。事实高置信，经济解释为分析推论。来源 https://ethereum.org/developers/docs/mev/ （2026-02-26更新）、https://ethereum.org/developers/docs/consensus-mechanisms/pos/rewards-and-penalties/ 。

4. **EIP-4844 为 blob 设置独立于执行 gas 的费市场，blob fee 被销毁。** L2 批量压缩发布减少每笔交易需要购买的 L1 资源；交易量与 L1 收费不成固定比例。机制高置信，Dencun 2024-03-13上线。来源 https://eips.ethereum.org/EIPS/eip-4844 。

5. **L2 使用 ETH 计费也不意味着费用全部销毁或归 ETH 普通持币者。** OP Stack规范规定L2 priority fee进入Sequencer Fee Vault、L2 base fee进入Base Fee Vault（明确不销毁）、L1-cost fee进入L1 Fee Vault，用于批次上链成本。足以反驳“L2全体交易费都是ETH收入”。2026-10-15检索规范，高置信；适用 OP Stack，不推广到所有L2。来源 https://specs.optimism.io/protocol/exec-engine.html#fees 。

6. **Fusaka 已上线，Glamsterdam尚不能当主网事实。** 官方roadmap：Pectra 2025-05-07、Fusaka 2025-12-03；Glamsterdam列Q4 2026 in development、Hegotá列2027。2026-09-28正文的Glamsterdam公告只安排Sepolia 2026-10-06 13:53:36 UTC，Hoodi/Mainnet TBD。URL路径日期09-17与正文日期09-28不同，以正文为准。高置信。来源 https://ethereum.org/roadmap/ 及 https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement 。

7. **Fusaka带来的供给扩张是客户价值，同时可能压低单位收费。** PeerDAS采样代替每节点下载所有blob；BPO允许重大升级之间调整容量；官方主网公告安排BPO1 target/max 10/15（2025-12-09）、BPO2 14/21（2026-01-07）。Fusaka官方当前页确认2025-12-03上线；不要再把Pectra的6/9当当前blob容量。60M是默认gas limit，不应仅凭公告断言每个当前区块限额。来源 https://ethereum.org/roadmap/fusaka/ （2026-09-26更新）、https://blog.ethereum.org/2025/11/06/fusaka-mainnet-announcement 。机制/已升级高置信；容量数取历史上线安排而非本次链上配置读数。

8. **EIP-7918为blob费提供与执行成本相联系的储备价机制，但不是美元收入保证。** Fusaka包括此EIP。它在blob fee低于执行成本基准时改变调整机制，避免费用长期失去价格信号；执行费用本身很低时，blob收入也可能很低。高置信，EIP创建2025-03-25，Final。来源 https://eips.ethereum.org/EIPS/eip-7918 及Fusaka官方公告。不要把它说成每个瞬间严格固定最低美元收费，规范承认快速执行费上涨时需若干区块追上。

9. **基金会自己的L1/L2路线表述也承认价值捕获尚须验证。** 2026-03-23 EF Platform团队说L2的主要价值转向差异化、定制和控制，L1也扩容；对ETH需求、网络效应等长期收益“需要实验、测量与分析验证”（意译）。不是网络增长必定利好币价的官方保证。该文的“blobs ~30% full”仅属于2026-03-23，不能当10月当日数据。来源 https://blog.ethereum.org/2026/03/23/l1-l2-ethereum 。高置信事实，投资含义为分析推论。

10. **当前近30日供应证据反驳“ETH正在必然通缩”。** Ultrasound API时间戳2026-10-15T05:50:35Z：近30日总销毁2487.4445450519265 ETH；按此窗口年化销毁30284.637336007207 ETH；年化发行1082513.6403416784 ETH；年化净供应增长0.008615629858212754，即约+0.86%。这是短窗口年化，不是未来预测。单源数据中等置信，等待市场代理独立核验。来源 https://ultrasound.money/api/v2/fees/burn-sums 与 https://ultrasound.money/api/v2/fees/gauge-rates 。关键口径：后端 https://github.com/ultrasoundmoney/eth-analysis-rs/blob/main/src/burn_sums/store.rs 第48行SQL同时加execution base fee与blob fee，因此v2 burn-sums已经包括blob，勿重复加总。

11. **有效质押约4376万ETH，但需区分有效余额、beacon总余额与存款合约累计额。** effective-balance-sum API在2026-10-15T05:49:47Z为43,763,362 ETH。Supply-parts在slot15434952/block26195933返回beaconBalancesSum 44199373467092917 gwei、beaconDepositsSum 90833001845995261 gwei、executionBalancesSum 168763875420869374814104311 wei。总供给公式是execution余额 + beacon余额 − 累计beacon deposits（避免重复计算），不能把存款合约累计额当当前质押。单源数据中等置信；确切金额计算由financial_rigor完成。来源 https://ultrasound.money/api/v2/fees/effective-balance-sum 、https://ultrasound.money/api/v2/fees/supply-parts ；公式/单位 https://github.com/ultrasoundmoney/frontend/blob/main/src/mainsite/api/supply-parts.ts 。

12. **资料的更新时间不代表所有示例参数是现状。** ethereum.org的Merge issuance页面最后更新2026-06-06，却保留14M质押、1700 ETH/day、16gwei抵消发行、32ETH effective max等旧例子；Pectra已允许有效余额最高2048ETH（最低仍32ETH）。不要把这些历史简化例子用作2026估值参数。高置信资料冲突。来源 https://ethereum.org/roadmap/merge/issuance/ 与 https://ethereum.org/roadmap/pectra/ 。

## 可选blob诊断与不能采用的数据

- https://ultrasound.money/api/fees/grouped-analysis-1 截至block26195936、最新块时间2026-10-15T05:51:23Z，单列blobFeeBurns近30日3.5371256500090307 ETH，近7日0.6700629791488082 ETH。数据为单源，旧版grouped API与v2在30日窗口存在缓存/口径差异（常规feesBurned近30日2499.51 ETH vs v2总销毁2487.44 ETH），**建议最终报告只用v2约+0.86%供应年化方向指标，不做blob精确占比**。
- validator-rewards接口给发行APR0.02503690189222894、tips0.0004492452744509923、MEV0.00047138733866695795，但无自身时间戳，annualReward是每validator Gwei，并存在32ETH旧模型口径；**不采用为当前可实现质押收益**。
- Beaconcha.in搜索缓存出现2.56% ETH.STORE、首页1.93% APR，但无法抓取有效当前日期正文，不能混为同一口径或当独立验证。

## 快照文件

- `/tmp/eth_ultrasound_20261015.json`：原始5个API数据与抓取时间（约2026-10-15T05:51:26Z）。
- `/tmp/eth_ultrasound_grouped_20261015.json`：旧版聚合API原始数据。

## 可用于报告的盈利桥

外部用户支付的L1执行费 → base fee销毁、priority fee给区块生产者；L2用户支付 → L2运营方费用账户，其中批次发布/证明所需的L1执行+blob费再流向Ethereum；共识发行 → 验证者安全报酬，同时增加供给。持币价值来自供给净变化及对ETH作为抵押品/结算资产/储值资产的需求。不能用TVL、稳定币名义流转额、L2交易笔数直接替代ETH持有人现金流。
