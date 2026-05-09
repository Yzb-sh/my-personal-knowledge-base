---
id: "202605061800"
title: "Hypothesis Testing Fundamentals"
created: "2026-05-06T18:00:00"
updated: "2026-05-07T19:00:00"
tags:
  - type/zettel
  - domain/math
  - mastery/2-familiar
aliases: []
---
# Hypothesis Testing Fundamentals

## Core Definition
假设检验是一种统计决策框架：通过量化"观察到的数据在零假设下有多不寻常"来判断是否有足够证据拒绝零假设。

## My Understanding
假设检验的核心逻辑是：如果因子无效（真实 IC=0），样本 IC 不一定等于 0，因为样本 IC 是有限数据的估计值。我需要知道在随机情况下，有多大概率能得到一个 IC 为 0.12 的因子。如果概率很大，因子可能是无效的；但如果只有很小很小的概率才能随机抽出一组 IC 为 0.12 的数据，那么因子可能是有效的。IC 为零是理论值（population parameter），而样本 IC 是实际值、估计值，所以很可能不为 0。t 统计量度量的是观察到的偏离是标准差的几倍，偏离越大越不像是碰巧出现的。ICIR = mean(IC)/std(IC)，t = ICIR × √T。

## Why It Matters
因子研究中几乎所有结论都需要统计显著性支持。单日 IC 是否为 0、长期平均 IC 是否显著——这些都是假设检验问题。理解 t 统计量和 ICIR 是读懂任何因子研究报告的前提。

## Technical Details

**假设检验框架**
- H₀（null hypothesis）：IC = 0，因子无效
- H₁（alternative hypothesis）：IC ≠ 0，因子有效
- 检验统计量：t = (观察值 - 零假设值) / SE

**标准误（Standard Error）的两种情况**
- 单截面 IC 的 SE：SE ≈ 1/√N（N 为截面资产数，相关系数在 ρ=0 下的理论性质）
- 多期 IC 均值的 SE：SE = std(IC)/√T（T 为时间期数，通用均值检验）

**ICIR 与 t 统计量**
- ICIR = mean(IC) / std(IC)
- t = ICIR × √T
- 例：ICIR = 0.25，T = 500 → t = 0.25 × √500 ≈ 5.59

**p-value**
- 在 H₀ 为真的前提下，观察到当前结果或更极端结果的概率
- p 越小，越有理由拒绝 H₀
- 常用阈值：α = 0.05（显著），α = 0.01（高度显著）

**经验法则**
- |t| > 2 → p < 0.05（显著）
- |t| > 3 → p < 0.01（高度显著）

**自相关的影响**（详见 [[Stationarity and ACF]]）
- i.i.d. 下 Var(mean) = σ²/T，SE = σ/√T
- 非独立下 Var(mean) = (σ²/T²) × [T + 2·Σ_{i<j} ρ(|i-j|)]，多了自相关修正项
- 正自相关 → Var(mean) > σ²/T → t 被高估
- ACF 检验：|ρ(k)| > 2/√T 说明存在显著自相关
- 修正：Newey-West 标准误，用 Bartlett 加权自协方差估计 σ²_NW，SE = √(σ²_NW/T)

## Application Example
面试场景：面试官给因子报告 Rank IC 均值 = 0.03，ICIR = 0.25，回测期 2 年（500 个交易日）。判断显著性：t = ICIR × √T = 0.25 × √500 ≈ 5.59，远超 3σ，非常显著。但需注意自相关可能使实际 t 小于此值。

## Common Misconceptions
- 混淆两种 SE 公式：单截面 IC 用 1/√N（相关系数理论结果），多期均值用 σ/√T（通用 CLT 结果），两者适用场景不同
- 混淆 √N 和 √T：N 是截面资产数，T 是时间维度数，t = ICIR × √T 用的是时间维度
- 用单截面 t 检验框架去检验多期均值：场景不同，SE 计算方式不同

## Connections
- [[MOC-Mathematics]] -- 属于统计学部分
- [[Expectation, Variance, and Covariance]] -- 方差和差公式 V(X+Y) 是理解自相关影响的基础
- [[Pearson vs Spearman Correlation]] -- IC 就是相关系数，假设检验判断 IC 是否显著
- [[Cross-Sectional vs Time-Series Data]] -- 两种 SE 对应截面检验和时间序列均值检验
- [[Multiple Testing Problem and Bonferroni Correction]] -- 检验多个因子时的假阳性问题
- [[Stationarity and ACF]] -- 自相关对 SE 的影响和 Newey-West 修正
