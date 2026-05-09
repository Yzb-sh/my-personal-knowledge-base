---
id: "202605092000"
title: "Turnover Analysis and Transaction Costs"
created: "2026-05-09T20:00"
updated: "2026-05-09T20:00"
tags:
  - type/zettel
  - domain/quant
  - domain/python
  - mastery/1-introduced
aliases: []
---
# Turnover Analysis and Transaction Costs

## Core Definition
换手率衡量分位组合成员在相邻调仓日之间的变化程度。通过计算换手率和交易成本，评估因子策略扣费后的真实盈利能力。

## My Understanding
分位组合每天重新排序分组，组成员不可能永远保持一致——变化程度越大，换手率越高，需要的手续费成本也就越高。换手率就是不重合的部分除以总成员数，简化为 1 - |A∩B|/|A|。IC 衰减快的因子排名变化快，换手率就高，扣完手续费可能就不赚钱了。降低调仓频率可以减成本，但也会牺牲信号时效性，需要在成本和收益之间找平衡。

## Why It Matters
IC 和分位数组合测试只告诉你因子的理论预测能力，但实际交易有手续费。一个 IC 很高但换手率也很高的因子，扣费后可能完全不赚钱。换手率分析是因子评估的最后一步，决定因子是否具有实际可交易性。

## Technical Details

**换手率定义**
- Turnover = 1 - |A ∩ B| / |A|，其中 A = T 日组成员集合，B = T+1 日组成员集合
- Turnover = 0：成员完全没变；Turnover = 1：全部换掉
- 因为 `pd.qcut` 每组大小固定，所以 |A| = |B|，公式可简化

**提取组成员集合**
```python
group_members = df.groupby(['date', 'group'])['symbol'].apply(set)
```
- `apply(set)` 将每个 (date, group) 的 symbol Series 转为 Python set
- `lambda x: set(x)` 等价于 `set`，可简化

**对齐相邻日期**
```python
gm = pd.DataFrame(group_members, columns=['symbols_t'])
gm['symbols_t_1'] = gm.groupby('group')['symbols_t'].shift(1)
```
- MultiIndex 为 (date, group)，需 `groupby('group')` 按组跨日期 shift
- `shift(1)` 向下移，当前行拿到上一行（昨天）的值
- 首行出现 NaN（没有前一天的数据）

**逐行计算换手率 — `apply(axis=1)`**
```python
gm['turnover'] = gm.apply(
    lambda x: 1 - len(x['symbols_t'] & x['symbols_t_1']) / len(x['symbols_t']),
    axis=1
)
```
- `df.apply(fn, axis=1)` 逐行操作，`fn` 收到的每一行是一个 Series
- `set_a & set_b` 是集合交集运算
- `len()` 和 `&` 作用在 Series 级别不能自动逐元素运算，必须用 `apply`

**汇总各组平均换手率**
```python
turnover_df = gm['turnover'].unstack()
mean_turnover = turnover_df.mean()
```

**交易成本计算**
```python
cost = (turnover_df[1] + turnover_df[5]) * 2 * 5e-4
net_ret = port_ret['long_short'] - cost
```
- Binance taker 费率 = 0.05% = 5e-4
- 每次换仓 = 卖旧 + 买新 = 2 笔交易，所以乘以 2
- 成本公式与 3C 中 long_short = ret_1 - ret_5 的标准一致（两组各满仓）

**扣费后 Sharpe 对比**
```python
sharpe_gross = port_ret['long_short'].mean() / port_ret['long_short'].std() * 365 ** 0.5
sharpe_net = net_ret.mean() / net_ret.std() * 365 ** 0.5
```

## Application Example
20 日动量因子的分位组合换手率分析：组 1 和组 5 的平均换手率分别为 0.35 和 0.30，每日成本 = (0.35 + 0.30) × 2 × 0.0005 = 0.065%。如果毛 Sharpe = 2.5，扣费后可能降至 1.8，说明因子在扣费后仍有盈利能力。若动量因子 IC 半衰期仅 2 天，换手率可能高达 0.6+，扣费后净收益可能接近零。

## Common Misconceptions
- 用 `groupby(['date', 'group']).shift()` 对齐相邻日期：每组只有 1 行，shift 无意义。应 `groupby('group')` 按组跨日期 shift
- `len(Series)` 和 `Series & Series` 不能逐元素操作 set：len 返回行数，& 做位运算。必须用 `apply(axis=1)` 逐行处理
- 成本只算 `turnover × fee_rate` 忘记乘 2：每次换仓涉及卖出旧仓和买入新仓两笔交易
- 成本公式用减法 `turnover_1 - turnover_5`：多空两端都要换仓，成本应相加
- `shift(-1)` vs `shift(1)` 混淆：`shift(1)` 向下移（拿到前一行/昨天的值），`shift(-1)` 向上移（拿到后一行/明天的值）
- 对 Series 用 `['col'] = value` 赋值：Series 没有 columns，需先转为 DataFrame

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子模型板块，因子评估体系
- [[MOC-Python]] -- apply(axis=1) 逐行操作、set 运算、unstack
- [[Quantile Portfolio Testing]] -- 换手率分析直接建立在分位数组合测试的基础上
- [[IC Decay and Half-Life Estimation]] -- IC 衰减速度决定换手率高低，半衰期短的因子换手率高
- [[IC Analysis and Significance Testing]] -- 换手率分析是 IC 分析和分位数测试之后的最后一步评估
- [[Cross-Sectional vs Time-Series Data]] -- 换手率是截面维度的成员变化度量
- [[Pandas GroupBy Transform and Apply]] -- apply(set) 和 apply(axis=1) 的基础

## References
- 因子分析教学 Module 3D（2026-05-09 会话）
