---
id: "202605072020"
title: "Factor Construction with Rolling Windows"
created: "2026-05-07T20:20"
updated: "2026-05-07T20:20"
tags:
  - type/zettel
  - domain/quant
  - mastery/1-introduced
aliases: []
---
# Factor Construction with Rolling Windows

## Core Definition
量化因子的构建可以用统一的代码模式实现：对面板数据按 symbol 分组，在滚动窗口上做聚合操作。不同因子的区别仅在于输入列、窗口大小和聚合函数。

## My Understanding
构建因子的代码模式是 df.groupby('symbol')[原始数据列].transform(lambda x: x.rolling(N).聚合操作())。所有因子都能用这个模式，因为它们的计算逻辑都是在每个 symbol 内部对某列数据取滚动窗口再做聚合——区别只在于取哪列、窗口多大、用什么聚合操作（sum/std/mean）。聚合操作的输入列决定因子含义：log_return_1d 求和是动量，return_1d 标准差是波动率，quote_volume 均值是成交金额。

## Why It Matters
因子是量化策略的核心输入。掌握统一的代码模式后，新增因子只需改变三个参数（列、窗口、操作），不需要重写框架代码。加密货币市场因子参数需要调整：高波动环境下动量窗口可能更短，流动性因子更重要。

## Technical Details

**统一代码模式**
```python
df['factor_name'] = df.groupby('symbol')[原始数据列].transform(
    lambda x: x.rolling(N).聚合操作()
)
```

**五个基础因子**

| 因子 | 原始数据列 | 窗口 | 聚合操作 | 经济含义 |
|------|-----------|------|---------|---------|
| 动量 mom_20 | log_return_1d | 20 | sum | 趋势延续 |
| 波动率 vol_20 | return_1d | 20 | std | 价格波动剧烈程度 |
| 成交金额 turnover_20d | quote_volume | 20 | mean | 市场活跃度 |
| Amihud非流动性 amihud_20d | abs(return_1d)/quote_volume | 20 | mean | 单位成交金额引起的价格变动 |
| 反转 rev_5 | -log_return_1d | 5 | sum | 短期过度反应的修正 |

**Amihud 非流动性因子**
- 日度值: amihud_1d = |return_1d| / quote_volume（行级运算，无需 groupby）
- 因子值: amihud_1d 的 20 日滚动均值
- 值越大 = 越不流动（少量资金就能引起大幅价格变动）

**动量 vs 反转**
- 动量: 过去涨的还会涨（中长期，20 日）
- 反转: 过去涨的会跌回来（短期，1-5 日）
- 反转因子 = 负的短期动量

## Application Example
Binance 加密货币面板数据（2025-03，458 币种）的因子构建：
```python
# 动量因子
df['mom_20'] = df.groupby('symbol')['log_return_1d'].transform(
    lambda x: x.rolling(20).sum()
)
# 波动率因子
df['vol_20'] = df.groupby('symbol')['return_1d'].transform(
    lambda x: x.rolling(20).std()
)
```

## Common Misconceptions
- 用简单收益率求和构建动量因子：简单收益率不满足可加性，应该用对数收益率
- 用 volume 而非 quote_volume 做截面成交金额因子：不同币种的 base currency 量纲不同，无法直接比较
- 忘记 groupby('symbol') 直接做 rolling：会把不同币种的数据串联计算

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子模型板块，因子构建
- [[MOC-Python]] -- 属于 Pandas 板块，Rolling Windows
- [[Simple and Log Returns]] -- 动量和反转因子基于对数收益率的可加性
- [[Pandas GroupBy Transform and Apply]] -- 因子构建的代码基础
- [[Volume vs Quote Volume]] -- 截面成交金额因子必须用 quote_volume
- [[Cross-Sectional Factor Standardization]] -- 因子构建后需要标准化才能截面比较

## References
- 因子分析教学 Module 2B（2026-05-07 会话）
