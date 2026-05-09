---
id: "202605091500"
title: "IC Decay and Half-Life Estimation"
created: "2026-05-09T15:00"
updated: "2026-05-09T15:00"
tags:
  - type/zettel
  - domain/quant
  - domain/python
  - mastery/1-introduced
aliases: []
---
# IC Decay and Half-Life Estimation

## Core Definition
IC 衰减曲线衡量因子预测能力随持有期限的衰减速度。半衰期是 IC 衰减到初始值一半所需的时间，反映因子信号的持久性。

## My Understanding
IC 衰减曲线就是同一个因子在不同前向期限（1d、2d、...、10d）上的截面 Rank IC。用累积收益率算就行，因为 Rank IC 只看排序不看绝对值。半衰期是 IC 衰减到初始值一半的时间，假设指数衰减 IC(h) = IC(0) × e^(-λh)，取对数变成 ln(IC) = ln(IC₀) - λh，做线性回归得到 -λ，半衰期 = ln(2)/λ。取 log 之前要先过滤掉 mean_ic ≤ 0 的行。也可以不拟合，直接找第一个低于 IC(0)/2 的天数（查表法）——拟合更抗噪声、能外推，查表更忠实于数据。画衰减曲线看的是 mean_IC（信号强度），不是 t_nw（显著性门槛）。

## Why It Matters
半衰期直接决定策略的最优持仓周期：如果因子半衰期只有 2 天，用 20 天持仓周期就没有意义。它也是比较不同因子信号持久性的标准化指标。

## Technical Details

**多期限前向收益率**
```python
for i in range(1, 11):
    df[f'fwd_return_{i}d'] = df.groupby('symbol')['close'].transform(
        lambda x: (x.shift(-i) - x) / x
    )
```

**IC 衰减曲线计算**
```python
results = []
for i in range(1, 11):
    ic_series = df.groupby('date')[['factor', f'fwd_return_{i}d']].apply(
        lambda x: x['factor'].corr(x[f'fwd_return_{i}d'], method='spearman')
    )
    stats = calc_ic_stats(ic_series)
    results.append({
        'ic_series': ic_series, 'days': i,
        'mean_ic': stats['mean_ic'], 't_nw': stats['t_nw']
    })
decay_df = pd.DataFrame(results)
```

**半衰期估算（指数拟合）**
```python
mask = decay_df['mean_ic'] > 0
filtered = decay_df[mask]
log_ic = np.log(filtered['mean_ic'])
coeffs = np.polyfit(filtered['days'], log_ic, 1)  # [slope, intercept]
half_life = np.log(2) / -coeffs[0]
```

**半衰期估算（直接查表）**
```python
threshold = decay_df['mean_ic'].iloc[0] / 2
below_half = decay_df[decay_df['mean_ic'] < threshold]
half_life = below_half['days'].iloc[0]
```

**np.polyfit(x, y, deg)** — 多项式最小二乘拟合
- 返回系数数组，从高次到低次：`deg=1` → `[slope, intercept]`
- `deg=2` → `[a, b, c]`，即 y = ax² + bx + c

**两种半衰期方法比较**
| 方法 | 优点 | 缺点 |
|------|------|------|
| 指数拟合 | 抗噪声、可外推 | 假设指数衰减 |
| 直接查表 | 忠实于数据 | 对噪声敏感、不能外推 |

## Application Example
20 日动量因子的 IC 衰减分析：对 458 个加密货币计算 1d~10d 的截面 Rank IC，画出 mean_IC 随天数的变化曲线。假设半衰期为 3 天，说明动量信号在 3 天后衰减一半，策略应以 2-3 天为持仓周期。

## Common Misconceptions
- `dict['key1','key2']` 不是取两个 key，而是用元组 `('key1','key2')` 当一个 key 查找 → 会 KeyError。正确写法：`d['key1'], d['key2']` 或先存变量再分别取
- `f'i'` 中没有花括号，生成的是字面字符串 `'i'`，不是变量 `i` 的值 → 应该写 `i` 或 `f'{i}'`
- `np.ln` / `np.lon` 不存在 → numpy 的自然对数是 `np.log`
- `np.polyfit` 返回 `[slope, intercept]`（高次到低次），不是 `[intercept, slope]` → 取斜率用 `[0]`
- `calc_ic_stats` 返回 dict，`['t_nw']` 已经是标量，不需要再加 `[0]`
- 过滤 DataFrame 后 index 不连续，用 `[0]` 是按 label 查找，可能找不到 → 用 `.iloc[0]` 按位置取

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子模型板块，因子评估
- [[MOC-Python]] -- 使用 groupby+apply、np.polyfit、DataFrame 构建
- [[IC Analysis and Significance Testing]] -- IC Decay 建立在 IC 分析基础上
- [[Factor Construction with Rolling Windows]] -- IC Decay 的输入是构建好的因子
- [[Pandas Series and DataFrame]] -- .iloc 索引用于查表法
- [[Stationarity and ACF]] -- 指数衰减与自相关函数的衰减形态类似
- [[Turnover Analysis and Transaction Costs]] -- IC 衰减速度直接决定换手率高低

## References
- 因子分析教学 Module 3B（2026-05-09 会话）
