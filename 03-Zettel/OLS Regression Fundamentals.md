---
id: "202605071500"
title: "OLS Regression Fundamentals"
created: "2026-05-07T15:00:00"
updated: "2026-05-07T15:00:00"
tags:
  - type/zettel
  - domain/math
  - mastery/2-familiar
aliases: []
---
# OLS Regression Fundamentals

## Core Definition
OLS（Ordinary Least Squares，普通最小二乘法）是一种参数估计方法，通过最小化残差平方和来拟合自变量与因变量之间的线性关系，求出最优的回归系数。

## My Understanding
OLS是一种参数估计方法，通过最小二乘法来拟合自变量与应变量，通过最小化残差平方和来求出最佳的拟合参数。

## Why It Matters
因子分析的核心工具。IC 衡量因子与收益的相关性，而 OLS 回归进一步告诉你"因子每变化 1 单位，收益预期变多少"（β），以及"这个模型解释了多少收益变异"（R²）。标准化后 β = ρ = IC，IC² = R²，这些等式把相关性、回归和因子解释力统一了起来。

## Technical Details

**回归方程**
- rᵢ = α + β·fᵢ + εᵢ
- α：截距，f=0 时 r 的基准值
- β：斜率，f 每变化 1 单位 r 的预期变化
- εᵢ：残差，模型无法解释的个体差异

**OLS 估计量**
- β = Cov(f, r) / Var(f)
- α = mean(r) - β·mean(f)
- α 的推导：对 Σ(rᵢ - α - β·fᵢ)² 关于 α 求偏导令其为 0

**β 与 ρ 的关系**
- β = ρ · σ_r / σ_f
- 标准化后（Z-score）：β = ρ = IC

**方差分解**
- Var(r) = Var(r̂) + Var(ε)，因为 Cov(r̂, ε) = 0
- R² = Var(r̂) / Var(r) = 1 - Var(ε) / Var(r) = ρ²

**关键性质**
- 回归线必过点 (mean(f), mean(r))
- Cov(r̂, ε) = 0：OLS 保证残差与预测值正交
- 一元回归中 R² = ρ²

## Application Example
截面因子分析中，对 458 个币的因子值 f 和未来收益 r 跑 OLS。β 告诉你因子每增加 1 个标准差，收益预期变化多少个标准差。R² = IC² 告诉你因子解释了百分之几的收益变异。单个因子 IC 通常在 0.03-0.10，对应 R² 仅 0.09%-1%，说明单因子解释力有限，需要多因子模型。

## Common Misconceptions
- 认为 β 衡量"f 相较 r 的变化程度"：β 衡量的是"f 每变 1 单位，r 变多少"，方向是 f→r
- 混淆 α 和 ε：α 是所有个体共同的固定基准，εᵢ 是每个个体独有的模型无法解释的部分
- 认为 OLS 只能做一元回归：OLS 是参数估计方法，可用于一元和多元线性回归
- 除以 Var(f) 还是 Var(r)：因为回归有方向性（用 f 预测 r），分母是 Var(f)

## Connections
- [[MOC-Mathematics]] -- 属于统计学部分
- [[Expectation, Variance, and Covariance]] -- β 的公式直接由 Cov 和 Var 构成
- [[Pearson vs Spearman Correlation]] -- β = ρ · σ_r/σ_f，标准化后 β = ρ；R² = ρ²
- [[Hypothesis Testing Fundamentals]] -- 回归系数的显著性检验建立在 t 检验框架上

## References
- 因子分析教学 Module 1C（2026-05-07 会话）
