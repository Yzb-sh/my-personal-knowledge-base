---
id: "202605072000"
title: "Simple and Log Returns"
created: "2026-05-07T20:00"
updated: "2026-05-07T20:00"
tags:
  - type/zettel
  - domain/quant
  - mastery/2-familiar
aliases: []
---
# Simple and Log Returns

## Core Definition
简单收益率衡量价格变动比例，对数收益率衡量价格变动的对数差。两者有精确的数学关系：log_return = log(1 + simple_return)。对数收益率具有可加性，多期对数收益率可以直接求和。

## My Understanding
简单收益率 r_t = (P_t - P_{t-1}) / P_{t-1}，可以变形为 P_t / P_{t-1} = 1 + r_t，所以对数收益率 R_t = log(1 + r_t)。对数收益率的可加性是因为 log(P_t/P_{t-1}) = log(P_t) - log(P_{t-1})，多期求和时中间项全部抵消，只剩 log(P_t) - log(P_{t-n})。简单收益率的多期公式是连乘 ∏(1+r_i)-1，不能直接相加。pct_change() 第一行返回的是 NaN（不是 0），NaN 应该保留不填充，填充 0 等于编造数据。前向收益率 return_1d_forward 表示从今天到明天的收益，等于 groupby('symbol') 后 shift(-1)。

## Why It Matters
因子研究的核心输入是收益率而非价格。对数收益率的可加性使得多期因子（如 20 日动量）的计算可以简化为滚动求和。不同因子需要选择不同收益率：动量用对数收益率（可加性），波动率用简单收益率（标准差定义）。

## Technical Details

**简单收益率（Simple Return）**
- r_t = (P_t - P_{t-1}) / P_{t-1}
- Pandas: `df.groupby('symbol')['close'].pct_change()`
- 多期: ∏(1+r_i) - 1（连乘，不能直接相加）
- 范围: (-1, +∞)

**对数收益率（Log Return）**
- R_t = log(P_t / P_{t-1}) = log(1 + r_t)
- Pandas: `np.log(1 + df['return_1d'])`
- 多期: ΣR_i = log(P_t / P_{t-n})（可加，中间项抵消）
- 范围: (-∞, +∞)

**面板数据注意事项**
- 必须先 groupby('symbol') 再计算，否则不同币种的数据会串行比较
- pct_change() 第一行为 NaN，保留不填充，Pandas 的 groupby/rank/corr 会自动跳过 NaN

**前向收益率（Forward Return）**
- 因子预测的目标变量
- df.groupby('symbol')['return_1d'].shift(-1)
- 表示 t 时刻的因子值对应 t+1 时刻实现的收益

## Application Example
构建 20 日动量因子时，用对数收益率的滚动求和：
```python
df['log_return_1d'] = np.log(1 + df.groupby('symbol')['close'].pct_change())
df['mom_20'] = df.groupby('symbol')['log_return_1d'].transform(lambda x: x.rolling(20).sum())
```

## Common Misconceptions
- 认为 pct_change() 第一行返回 0：实际返回 NaN，0 意味着"收益率为零"，NaN 意味着"不知道"
- 认为 fillna(0) 是合理的 NaN 处理：在因子研究中，编造数据会污染后续 IC 计算和截面分析
- 混淆简单收益率和对数收益率的多期计算：简单收益率必须连乘，对数收益率可以相加

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子研究的数据基础
- [[Cross-Sectional vs Time-Series Data]] -- 收益率计算是时序操作，截面比较需要面板数据分组
- [[Pandas Series and DataFrame]] -- pct_change() 是 DataFrame/Series 的内置方法
- [[Factor Construction with Rolling Windows]] -- 对数收益率的可加性是滚动因子计算的基础
- [[OLS Regression Fundamentals]] -- 回归分析的因变量通常是收益率

## References
- 因子分析教学 Module 2A（2026-05-07 会话）
