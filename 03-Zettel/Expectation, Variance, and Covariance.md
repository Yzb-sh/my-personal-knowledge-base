---
id: "202605061430"
title: "Expectation, Variance, and Covariance"
created: "2026-05-06T14:30:00"
updated: "2026-05-07T15:00:00"
tags:
  - type/zettel
  - domain/math
  - mastery/2-familiar
aliases: []
---
# Expectation, Variance, and Covariance

## Core Definition
概率论中描述随机变量分布特征的三个核心统计量：期望描述中心位置，方差描述离散程度，协方差描述两个变量的协同变化方向。

## My Understanding
期望是基于概率分布的理论值，是对所有可能结果按概率加权求和。历史数据算出来的样本均值只是期望的近似估计，两者是不同的概念。方差度量随机变量偏离期望的程度，取平方而非绝对值是为了保证可微性和代数展开的简洁性。协方差把方差中"变量自身偏离"的第二个因子换成另一个变量，从而度量两个变量的协同变化。

## Why It Matters
这三个量是量化研究的数学基石。因子 IC 是因子值与收益率的协方差标准化后的结果，风险模型中的协方差矩阵直接决定组合权重，理解它们的数学定义和推导过程是理解一切下游概念的前提。

## Technical Details

**期望 (Expected Value)**
- 离散：E[X] = Σ xᵢ · pᵢ
- 连续：E[X] = ∫ x · f(x) dx
- 性质：线性性 E[X+Y] = E[X] + E[Y]；E[cX] = cE[X]

**方差 (Variance)**
- 定义：V[X] = E[(X - E[X])²]
- 计算公式：V[X] = E[X²] - (E[X])²
- 取平方的原因：(1) x² 处处可微，|x| 在 0 处不可导，便于优化 (2) 展开后得到干净的 E[X²] - (E[X])² 表达式

**协方差 (Covariance)**
- 定义：Cov(X, Y) = E[(X - E[X])(Y - E[Y])]
- 计算公式：Cov(X, Y) = E[XY] - E[X]E[Y]
- X 与 Y 独立时 Cov = 0（反之不一定成立）

**线性变换性质**
- E[aX + b] = a·E[X] + b
- Var(aX + b) = a²·Var(X)
- 应用：Z-score 标准化 Z = (X-μ)/σ → E[Z] = 0, Var(Z) = 1

**方差和差公式**
- V(X+Y) = V[X] + V[Y] + 2Cov(X, Y)
- V(X-Y) = V[X] + V[Y] - 2Cov(X, Y)

## Application Example
截面因子 IC 的计算：在某个时间截面上，对 N 个资产的因子值 f 和未来收益 r 计算 Cov(f, r)，再除以 σ_f · σ_r 得到 Pearson 相关系数。理解协方差的展开形式有助于理解后续的因子合成权重（IC 加权、ICIR 加权）。

## Common Misconceptions
- 混淆期望与样本均值：期望是关于概率分布的理论量，样本均值是从数据中计算的估计量
- 方差定义中漏掉概率权重 pᵢ：V[X] = Σ(xᵢ - E[X])² · pᵢ，不是简单的偏差平方和
- 认为 Cov(X,Y) = 0 意味着 X 和 Y 独立：协方差为零只说明没有线性关系，不排除非线性依赖

## Connections
- [[MOC-Mathematics]] -- 属于概率论部分
- [[Pearson vs Spearman Correlation]] -- 相关系数是协方差的标准化形式
- [[OLS Regression Fundamentals]] -- β = Cov(f,r)/Var(f)，回归斜率由协方差和方差构成
- [[Cross-Sectional vs Time-Series Data]] -- 截面 IC 的计算基于截面协方差
