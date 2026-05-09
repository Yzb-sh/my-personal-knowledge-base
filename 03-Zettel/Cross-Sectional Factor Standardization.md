---
id: "202605072030"
title: "Cross-Sectional Factor Standardization"
created: "2026-05-07T20:30"
updated: "2026-05-07T20:30"
tags:
  - type/zettel
  - domain/quant
  - mastery/1-introduced
aliases: []
---
# Cross-Sectional Factor Standardization

## Core Definition
因子标准化是将不同量纲的因子值转换到同一尺度，使得截面比较和 IC 计算有意义。常用方法有 Z-score、Rank 百分位和 MinMax，其中 Rank 对异常值最鲁棒。标准化在截面维度进行（同一天所有资产），而非时序维度。

## My Understanding
rank 的方式能够提高异常值的鲁棒性，异常值不会怎么影响其他值，但是如果用 minmax 方式，异常值会极度影响每个值的计算，因为分母中有最大值。Winsorize 是在标准化之前的预处理步骤，把超过百分位阈值的极端值截断。业界标准流水线是先 Winsorize 再 Rank，双重保护。标准化必须是截面维度的（按 date 分组），因为因子研究的目的是在同一天比较所有币种的信号强弱。

## Why It Matters
原始因子值量纲差异巨大（BTC 动量 0.03 vs 山寨币 0.6），不标准化就无法做截面排名和 IC 分析。极端值会严重扭曲 Z-score 和 MinMax 的结果，导致大部分正常值被压缩到很小的范围内，失去区分度。

## Technical Details

**截面 Winsorize（预处理）**
```python
df['return_1d'] = df.groupby('date')['return_1d'].transform(
    lambda x: x.clip(x.quantile(0.01), x.quantile(0.99))
)
```
- 截面维度：在同一天比较所有币种判断谁是极端值
- 不是删除，而是把极端值截断到阈值上
- quantile(0.01) 表示从小到大排序的第 1% 位置

**Z-score 标准化**
```python
df['mom_20_z'] = df.groupby('date')['mom_20'].transform(
    lambda x: (x - x.mean()) / x.std()
)
```
- 结果近似标准正态分布，大部分值在 [-3, 3]
- 受极端值影响中等（mean 和 std 都会被极端值拉偏）

**Rank 百分位**
```python
df['mom_20_rank'] = df.groupby('date')['mom_20'].transform(
    lambda x: x.rank(ascending=False, pct=True)
)
```
- ascending=False: 值最大 → 排名最高
- pct=True: 排名转为 [0, 1] 的百分位值
- 只看相对位置，完全不受极端值影响

**MinMax 标准化**
```python
df['mom_20_mm'] = df.groupby('date')['mom_20'].transform(
    lambda x: (x - x.min()) / (x.max() - x.min())
)
```
- 缩放到 [0, 1]
- 最受极端值影响：1 个极端 max 会把其他值全部压缩

**三种方法鲁棒性排序**
Rank > Z-score > MinMax

**业界标准流水线**
Winsorize → Rank（先截尾再排名，双重保护）

## Application Example
加密货币因子标准化：458 个币种的动量因子值差异巨大，1 个被拉盘的小币种动量可能到 5.0，而 BTC 只有 0.03。先截面 Winsorize 截掉极端值，再用 Rank 百分位标准化，所有币种的因子值都在 [0, 1] 且不受异常值影响。

## Common Misconceptions
- 对每个币种用自己历史做时序标准化：因子研究要做截面比较（今天谁信号最强），不是时序比较
- 用 fillna(0) 处理 NaN：编造数据，0 不等于"不知道"
- 认为 Winsorize 和 Rank 只需要选一个：Winsorize 保护 Z-score/MinMax，Rank 本身已经鲁棒，两者组合是最佳实践

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子模型板块，因子预处理
- [[Cross-Sectional vs Time-Series Data]] -- 因子标准化是截面操作
- [[Factor Construction with Rolling Windows]] -- 因子构建后的必要步骤
- [[Simple and Log Returns]] -- 收益率的截面 Winsorize 预处理
- [[Pandas GroupBy Transform and Apply]] -- 标准化代码基于 groupby+transform

## References
- 因子分析教学 Module 2C（2026-05-07 会话）
