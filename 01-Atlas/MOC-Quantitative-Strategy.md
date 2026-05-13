---
id: "moc-20260427-quant"
title: "MOC-Quantitative-Strategy"
created: "2026-04-27"
updated: "2026-05-10"
tags:
  - type/structure
---
# MOC-Quantitative-Strategy

量化策略研发全链路知识体系。

## Research Foundation (研究基础)
- [[...]] -- Research Workflow (研究工作流：想法→假设→测试→迭代)
- [[...]] -- Data Sources and Data Quality (数据来源与数据质量)
- [[L2 Market Data Storage Strategy]] -- L2行情数据存储策略（ClickHouse + Parquet）
- [[Parquet File Format]] -- Parquet文件格式（L2数据的存储格式）
- [[...]] -- Feature Engineering (特征工程)
- [[...]] -- Signal vs Noise (信号与噪声)

## Factor Models (因子模型)
- [[...]] -- Single-Factor Models CAPM Beta (单因子模型：CAPM, Beta)
- [[...]] -- Fama-French Multi-Factor Models (Fama-French 多因子模型)
- [[Factor Construction with Rolling Windows]] -- Factor Construction (因子构建：动量、波动率、成交金额、Amihud、反转)
- [[IC Analysis and Significance Testing]] -- Factor Testing IC IR Turnover (因子测试：截面IC计算、Rank IC、显著性检验、Newey-West修正)
- [[IC Decay and Half-Life Estimation]] -- Factor Decay and Half-Life (因子衰减：IC衰减曲线、指数衰减拟合、半衰期估算、持仓周期决策)
- [[Quantile Portfolio Testing]] -- Factor Quantile Portfolio Test (分位数组合测试：pd.qcut分组、unstack宽格式、多空价差、单调性检验、cumprod净值、年化Sharpe)
- [[Turnover Analysis and Transaction Costs]] -- Turnover and Transaction Cost Analysis (换手率分析：成员集合变化、apply(axis=1)逐行运算、交易成本建模、净Sharpe评估、IC衰减与换手率关系)
- [[Factor Combination Methods]] -- Factor Combination and Selection (因子组合与选择：等权/IC/ICIR加权、前视偏差、定期更新权重)
- [[...]] -- Cross-Sectional vs Time-Series Factors (截面因子 vs 时序因子)

## Strategy Development (策略开发)
- [[...]] -- Mean Reversion Strategies (均值回归策略)
- [[...]] -- Momentum Strategies (动量策略)
- [[...]] -- Statistical Arbitrage Pairs Trading (统计套利/配对交易)
- [[...]] -- Event-Driven Strategies (事件驱动策略)
- [[...]] -- Machine Learning in Strategy Development (机器学习在策略开发中的应用)

## Backtesting (回测)
- [[...]] -- Backtesting Framework Design (回测框架设计)
- [[Backtesting with Transaction Costs]] -- Performance Metrics and Backtesting (绩效指标与回测：cumprod净值、cummax回撤、Sharpe、Calmar、交易成本)
- [[...]] -- Transaction Cost Modeling (交易成本建模)
- [[...]] -- Slippage and Market Impact (滑点与市场冲击)
- [[...]] -- Overfitting Detection (过拟合检测：walk-forward, cross-validation)
- [[...]] -- Survivorship Bias (幸存者偏差)
- [[...]] -- Look-Ahead Bias (前视偏差)

## Risk Management (风险管理)
- [[...]] -- Portfolio Variance and Covariance (组合方差与协方差)
- [[...]] -- Value at Risk VaR (风险价值)
- [[...]] -- Expected Shortfall CVaR (条件风险价值)
- [[...]] -- Stress Testing (压力测试)
- [[Inverse Volatility Position Sizing]] -- Position Sizing Inverse Volatility (仓位管理：反波动率加权、多空分配、.loc赋值)
- [[...]] -- Correlation Regime Detection (相关性体制检测)

## Portfolio Construction (组合构建)
- [[...]] -- Mean-Variance Optimization Markowitz (均值方差优化)
- [[...]] -- Risk Budgeting and Risk Parity (风险预算与风险平价)
- [[...]] -- Black-Litterman Model (Black-Litterman 模型)
- [[...]] -- Rebalancing Strategies (再平衡策略)
- [[...]] -- Constraint Handling (约束处理)

## Execution (执行)
- [[...]] -- Order Types (订单类型)
- [[...]] -- Market Microstructure Basics (市场微观结构基础)
- [[...]] -- Execution Algorithms VWAP TWAP (执行算法)
- [[...]] -- Transaction Cost Analysis TCA (交易成本分析)

## Cross-Domain Connections
- [[L2 Market Data Storage Strategy]] (量化↔SQL/Python) -- 数据库选型和Parquet存储方案
- [[MongoDB vs MySQL vs ClickHouse]] (量化↔SQL) -- L2数据为什么选ClickHouse

## See Also
- [[MOC-Home]] -- 返回主索引
- [[MOC-Mathematics]] -- 策略背后的数学原理
- [[MOC-Python]] -- 策略的 Python 实现
- [[MOC-SQL]] -- 数据获取与处理

## Gaps & Next Steps
- [ ] 确定当前最需要深入的策略领域
- [ ] 选择参考书籍或论文
