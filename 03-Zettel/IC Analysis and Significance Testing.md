---
id: "202605082100"
title: "IC Analysis and Significance Testing"
created: "2026-05-08T21:00"
updated: "2026-05-09T15:00"
tags:
  - type/zettel
  - domain/quant
  - domain/python
  - mastery/1-introduced
aliases: []
---
# IC Analysis and Significance Testing

## Core Definition
IC（Information Coefficient）是因子值与未来收益率之间的截面相关系数，衡量因子的预测能力。通过计算每期 IC 并做显著性检验（t 检验 + Newey-West 自相关修正），可以判断因子是否有效。

## My Understanding
IC 本质上就是衡量因子值和未来收益率之间相关性的指标。计算方法是每天对所有资产算一次截面相关系数，得到一个 IC 时间序列，然后检验这个序列的均值是否显著不为零。Rank IC（Spearman）比 Normal IC（Pearson）更常用，因为因子和收益的关系往往单调但不线性，而且极端值多。IC 可以是时序的（单资产自己的因子值和收益率的时序相关），也可以是截面的（同一天所有资产的因子值和收益率的横向相关），但因子选币用的是截面 IC。

## Why It Matters
IC 是因子评估体系的第一步，也是最核心的指标。一个因子是否值得研究，首先要看 IC 是否显著。但单纯的 IC 均值不够——IC 的波动（ICIR）和自相关性（需要 Newey-West 修正）同样重要，否则会高估因子的显著性。

## Technical Details

**每日截面 Rank IC 计算**
```python
ic_series = df.groupby('date')[['factor', 'fwd_return_1d']].apply(
    lambda x: x['factor'].corr(x['fwd_return_1d'], method='spearman')
)
```
- `groupby('date')` 按天分组，每组是所有资产的截面
- `apply` 返回每组一个值（每天一个 IC），不是 `transform`（广播回原始行数）
- `method='spearman'` 使用秩相关，对极端值鲁棒

**IC 显著性检验**

IID 假设下的 t 统计量：
- ICIR = mean(IC) / std(IC)
- t_iid = ICIR × √T

Newey-West 自相关修正：
- 滞后阶数 L ≈ T^(1/3)
- Bartlett 权重 w(k) = 1 - k/(L+1)
- 自协方差 γ(k) = ic_series.cov(ic_series.shift(k))
- SE_NW = √((γ(0) + 2×Σ_{k=1}^{L} w(k)×γ(k)) / T)
- t_nw = mean(IC) / SE_NW

p-value（双尾检验）：
```python
from scipy import stats
p = 2 * stats.t.sf(abs(t_nw), df=T-1)
```

**完整函数**
```python
import scipy.stats
import pandas as pd
from math import sqrt

def calc_ic_stats(ic_series: pd.Series) -> dict:
    T = len(ic_series)
    if T <= 2:
        return None
    L = int(T ** (1/3))
    mean_ic = ic_series.mean()
    std_ic = ic_series.std()
    icir = mean_ic / std_ic
    t_iid = icir * sqrt(T)
    gamma = []
    for i in range(L + 1):
        gamma.append((1 - i / (L + 1)) * ic_series.cov(ic_series.shift(i)))
    se_nw = sqrt((2 * sum(gamma) - gamma[0]) / T)
    t_nw = mean_ic / se_nw
    p_nw = 2 * scipy.stats.t.sf(abs(t_nw), T - 1)
    return {
        'mean_ic': mean_ic, 'std_ic': std_ic, 'icir': icir,
        't_iid': t_iid, 't_nw': t_nw, 'p_nw': p_nw
    }
```

**Python 注意事项**
- `groupby()[[col1, col2]]` 双括号选多列，单括号已废弃
- `apply` 返回每组一个值，`transform` 广播回原始行数
- `**` 是幂运算，`^` 是按位异或
- `abs` 是内置函数，不需要 import
- `import scipy.stats` 才能使用 `scipy.stats.t.sf`
- `list.append()` 添加元素，不能对空 list 用 `list[i] = ...`

## Application Example
加密货币因子研究场景：458 个币种的面板数据，计算 20 日动量因子的截面 Rank IC。得到 60 个交易日的 IC 序列后，用 Newey-West 修正的 t 检验判断因子是否显著。如果 t_nw > 2（p < 0.05），认为因子有效。

## Common Misconceptions
- 混淆 `.corr()` 和 `.cov()`：`.corr()` 返回相关系数（-1 到 1），`.cov()` 返回协方差（无固定范围）。Newey-West 需要的是自协方差 γ(k)，用 `.cov()`
- 对 IC 序列用 `transform` 而不是 `apply`：`transform` 会广播回原始行数，而 IC 应该每天一个值
- 忘记在 `scipy.stats.t.sf` 中使用 `abs(t_nw)`：负的 t 值会导致 p > 1

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子模型板块，因子评估
- [[MOC-Python]] -- 属于 Pandas 板块，groupby apply
- [[Pearson vs Spearman Correlation]] -- IC 的数学基础是相关系数
- [[Cross-Sectional vs Time-Series Data]] -- 截面 IC 是截面维度的操作
- [[Hypothesis Testing Fundamentals]] -- IC 显著性检验的统计框架
- [[Stationarity and ACF]] -- Newey-West 修正的理论基础
- [[Factor Construction with Rolling Windows]] -- IC 分析的输入是构建好的因子
- [[Cross-Sectional Factor Standardization]] -- 标准化后的因子才能做截面 IC 计算
- [[Pandas GroupBy Transform and Apply]] -- IC 计算代码基于 groupby+apply
- [[IC Decay and Half-Life Estimation]] -- IC Decay 是 IC 分析在多期限上的延伸
- [[Turnover Analysis and Transaction Costs]] -- 换手率分析是 IC 评估之后的可交易性验证

## References
- 因子分析教学 Module 3A（2026-05-08 会话）
