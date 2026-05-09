---
id: "202605061431"
title: "Pearson vs Spearman Correlation"
created: "2026-05-06T14:31:00"
updated: "2026-05-07T15:00:00"
tags:
  - type/zettel
  - domain/math
  - mastery/2-familiar
aliases: []
---
# Pearson vs Spearman Correlation

## Core Definition
Pearson 相关系数量化两组变量之间的线性关系强度，Spearman 秩相关系数量化单调关系强度。两者都取值于 [-1, 1]，但适用场景不同。

## My Understanding
Pearson 相关是协方差除以两个标准差的乘积，消除量纲后变成可跨资产比较的纯数值。它的本质是度量线性关系，如果因子和收益的关系是单调弯曲的，Pearson 会低估。Spearman 的思路是不看具体值，只看排名——把因子值和收益率各自换成排名序列后再算 Pearson 相关。这样消除了极端值的影响，对单调但不严格线性的关系更稳健。在因子测试中，Spearman IC（Rank IC）比 Pearson IC 更常用。

## Why It Matters
因子 IC 是因子研究中最核心的评价指标。加密货币数据极端值多、因子与收益的关系往往单调但不线性，因此 Rank IC 比 Normal IC 更稳定可靠。理解两种相关的区别是正确解读 IC 值的前提。

## Technical Details

**Pearson 相关系数**
- 定义：ρ(X, Y) = Cov(X, Y) / (σ_X · σ_Y)
- 取值范围：[-1, 1]
- |ρ| ≤ 1 的证明：对任意 λ，V[X - λY] = V[X] + λ²V[Y] - 2λCov(X,Y) ≥ 0。该二次函数恒非负，故判别式 4Cov² - 4V[X]V[Y] ≤ 0，即 Cov² ≤ σ_X²σ_Y²，得 |ρ| ≤ 1。

**Spearman 秩相关系数**
- 定义：对 X 和 Y 分别取排名 rank(X) 和 rank(Y)，然后计算 Pearson(rank(X), rank(Y))
- 度量单调关系，不需要线性假设
- 对极端值鲁棒（极端值无论多大，排名只变化 1）

**对比**
| 特征 | Pearson | Spearman |
|------|---------|----------|
| 度量关系 | 线性 | 单调 |
| 对极端值 | 敏感 | 鲁棒 |
| 因子测试中 | Normal IC | Rank IC（更常用） |

## Application Example
加密货币因子测试场景：458 个币的因子值与未来收益率。如果散点图显示单调递增但弯曲的关系，且存在极端值，Spearman IC 能更准确反映因子的预测能力。实际研究中通常同时报告两种 IC，重点关注 Rank IC。

## Common Misconceptions
- 试图用 AM-GM 不等式证明 |ρ| ≤ 1：(V[X]+V[Y])/2 ≥ σ_Xσ_Y 只给出一个比 1 更松的上界，无法证得 |ρ| ≤ 1。正确证法是利用 V[X - λY] ≥ 0 的判别式。
- 认为 Spearman 完全替代 Pearson：如果关系不是单调的（如 U 型），Spearman 也捕捉不到。

## Connections
- [[MOC-Mathematics]] -- 属于概率论部分（期望、方差、协方差的直接应用）
- [[Expectation, Variance, and Covariance]] -- 相关系数建立在协方差和标准差之上
- [[OLS Regression Fundamentals]] -- β = ρ·σ_r/σ_f，标准化后 β = ρ；R² = ρ²
- [[Cross-Sectional vs Time-Series Data]] -- 截面 IC 的计算方法选择
