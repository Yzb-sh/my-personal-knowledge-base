---
id: "202605071900"
title: "Stationarity and ACF"
created: "2026-05-07T19:00:00"
updated: "2026-05-07T19:00:00"
tags:
  - type/zettel
  - domain/math
  - mastery/2-familiar
aliases: []
---
# Stationarity and ACF

## Core Definition
平稳性（Stationarity）指时间序列的统计性质不随时间平移而改变；自相关函数 ACF ρ(k) 度量一个序列与自身滞后 k 期版本之间的线性相关性，本质就是 Pearson 相关系数。

## My Understanding
平稳性意味着市场结构没有发生本质变化——如果前半月是牛市、后半月是震荡市，因子表现不同，那平稳性就不成立。在平稳性假设下，Cov(IC_i, IC_j) 只取决于两个时间点的距离 |i-j|，不取决于绝对位置。ACF ρ(k) = γ(k)/γ(0) 在平稳性下和 Pearson 相关系数完全一样：σ_X = σ_Y = σ，分母就是 σ² = Var(IC_t)。如果序列有正自相关，Var(mean) 会比 i.i.d. 假设下的 σ²/T 更大，导致真实的 t 统计量比 i.i.d. 公式算出来的更小——我们一直在高估因子的显著性。

## Why It Matters
因子 IC 的 t 检验公式 t = ICIR × √T 依赖 SE = σ/√T，而这个公式只在 i.i.d. 下成立。实际 IC 序列常有自相关，导致 SE 被低估、t 被高估。Newey-West 修正用加权的样本自协方差修正 SE，是因子显著性检验的标准工具。

## Technical Details

**平稳性**
- 统计性质（均值、方差、协方差）不随时间平移改变
- 关键推论：γ(k) = Cov(X_t, X_{t+k}) 只依赖 k，不依赖 t
- 反例：牛市期和震荡期的 IC 分布不同 → 非平稳

**自协方差函数**
- γ(k) = Cov(X_t, X_{t+k})
- γ(0) = Var(X_t) = σ²

**自相关函数 ACF**
- ρ(k) = γ(k) / γ(0) = Cov(X_t, X_{t+k}) / Var(X_t)
- 平稳性下：σ_t = σ_{t+k} = σ，所以 ρ(k) = Cov / (σ·σ) = Pearson 相关系数
- ρ(0) = 1

**Var(mean) 的自相关修正**
- i.i.d. 下：Var(mean) = σ²/T
- 非独立下：Var(mean) = (σ²/T²) × [T + 2·Σ_{i<j} ρ(|i-j|)]
- 正自相关 → 修正项为正 → Var(mean) > σ²/T → SE 被低估 → t 被高估

**ACF 显著性检验**
- H₀: ρ(k) = 0（无自相关）
- SE ≈ 1/√T
- 判断规则：|ρ(k)| > 2/√T → 显著

**Newey-West 标准误**
- σ²_NW = γ̂(0) + 2·Σ_{k=1}^{L} (1 - k/(L+1))·γ̂(k)
- 权重 w(k) = 1 - k/(L+1) 从 1 衰减到 0（Bartlett kernel）
- 修正后 SE = √(σ²_NW / T)
- L 的选择：偏差-方差权衡，L 太小修正不足，L 太大估计不稳定；常用 L ≈ T^(1/3)

## Application Example
面试场景：用 ICIR × √T 算出 t = 5.6 看似很显著。检验步骤：(1) 计算前几阶 ACF，若 |ρ(k)| > 2/√T 则存在自相关；(2) 用 Newey-West 修正 SE，得到更保守的 t 值。加密货币 24/7 交易、因子 IC 日频计算，相邻日 IC 常有正自相关，修正后 t 可能从 5.6 降到 3-4。

## Common Misconceptions
- 混淆 SE = std/√T 与 SE = Var/√T：量纲不对，SE 应与 IC 同量纲，std 才对
- 认为 ACF 是一个新的相关系数定义：它就是 Pearson，只是计算对象是同一序列的不同滞后
- 忽略平稳性假设：如果市场 regime 发生变化，ACF 的定义基础就不成立

## Connections
- [[MOC-Mathematics]] -- 属于统计学部分，时间序列基础
- [[Hypothesis Testing Fundamentals]] -- ACF 和 Newey-West 是 IC 显著性检验的修正工具
- [[Expectation, Variance, and Covariance]] -- 方差和公式 Var(X+Y) 是推导 Var(mean) 修正项的基础
- [[Pearson vs Spearman Correlation]] -- ACF ρ(k) 本质就是 Pearson 相关系数
- [[Cross-Sectional vs Time-Series Data]] -- 时间序列分析属于时序维度操作

## References
- 因子分析教学 Module 1D（2026-05-07 会话）
