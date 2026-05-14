---
id: "proj-20260430"
title: "Factor Analysis Teaching Plan"
created: "2026-04-30"
updated: "2026-05-11"
tags:
  - type/project
  - domain/quant
  - mastery/2-applying
status: active
---
# Factor Analysis Teaching Plan — 因子分析跨域教学方案

**目标**: 掌握因子分析理论与手写代码能力，能独立研究Binance加密货币数据

## 学员水平
- 数学/统计：有基本概念，未深入推导
- Python/Pandas：中等水平，会用groupby/merge/rolling

## 进度跟踪

### Module 0: 环境搭建与数据探索 — [completed]
- [x] 探索Binance 1m K线数据结构
- [x] 理解加密货币市场特性 vs A股
- [x] 搭建因子研究Python环境
- [x] 编写数据加载工具函数（merge_1m_2_1d, build_daily_panel）
- [x] 构建了 2025-03 日线面板（13,748行，458币种）

### Module 1: 数学基础 — 相关性与回归 — [completed]
- [x] 1A: 相关性分析（Pearson vs Spearman）
- [x] 1B: 假设检验（t检验、多重比较校正）
- [x] 1C: OLS回归（直觉、残差、R²）
- [x] 1D: 时间序列基础（平稳性、ACF、Newey-West）

### Module 2: 数据处理与因子构建 — [completed]
- [x] 2A: 收益率计算与预处理
- [x] 2B: 基础因子构建（动量、反转、波动率、成交量、流动性）
- [x] 2C: 因子标准化（Z-score、截面、排名）

### Module 3: 因子评估体系 — [completed]
- [x] 3A: IC分析（计算、显著性）
- [x] 3B: IR与因子质量（衰减、半衰期）
- [x] 3C: 分位数组合测试
- [x] 3D: 换手率分析

### Module 4: 因子组合与策略构建 — [completed]
- [x] 4A: 因子合成（等权、IC加权、ICIR加权）
- [x] 4B: 策略构建（多空、仓位管理、再平衡）
- [x] 4C: 回测基础（Sharpe、最大回撤、成本建模）

### Module 5: 实战项目 — 动量因子完整研究 — [in-progress]
- [x] 制定详细研究计划书（已完成，见 [[momentum-factor-research-plan]]）
- [x] 确定研究参数（FREQUENCY=15min/5min, START_DATE=2023-01-01, N_SYMBOLS=200, 动态宇宙, 滚动窗口训练）
- [x] 确定因子定义（6大类62变体: CS/RA/VW/CON/ED/UD，已核实无方向性因子）
- [x] 确定分析框架（3阶段: 因子发现→因子深入→Walk-Forward OOS）
- [x] 计划审核与修订（多重检验FDR校正、比例制窗口步长WINDOW_STEP_RATIO=1/3、基准对比、Regime分析、风险管理规则）
- [ ] Step 5.0: 数据探索与理解（阶段0，2-3天）— 数据质量、效率基线
- [ ] Step 5.1: 数据管线 — 面板构建 + 宇宙筛选
- [ ] Step 5.2: 因子构建 — 6大类62变体 + 标准化
- [ ] Step 5.3: 滚动IC分析 — 多尺度窗口, PIR/Mean IC/IC Sharpe筛选 + FDR多重检验校正
- [ ] Step 5.4: IC衰减 + 分位数组合 + 换手率 + 基准对比 + Regime分析
- [ ] Step 5.5: 因子合成 + 仓位管理 + 风险管理规则（仓位限制、集中度、回撤熔断）
- [ ] Step 5.6: Walk-Forward OOS验证 + Regime分段报告
- [ ] Step 5.7: 敏感性分析（含 WINDOW_STEP_RATIO 1/3 vs 1/2）
- [ ] Step 5.8: 效率优化（阶段2）— 性能剖析、瓶颈优化、DuckDB/NumPy/并行化
- [ ] 研究结论与报告

### Module 6: 高级主题（可选） — [not-started]

## 关键资源
- 参考资料: `临时/因子研究1/` (因子研究学习清单.md 等)
- 数据: `crypto-quant-fund/data/processed/binance_1m_klines/` (~50万parquet, 2020-2025)
- MOC: [[MOC-Python]], [[MOC-Mathematics]], [[MOC-Quantitative-Strategy]]
- 教学命令: /drill-math (数学), /drill-code (编程)

## 加密货币适配要点
- 24/7交易 → UTC日切或自定义bar
- 无涨跌停 → 不需处理
- 永续合约 → 天然多空
- 低交易成本 → maker/taker费率
- 高波动 → 因子参数需调整
- ~200-300活跃资产 → 截面较窄

## 会话日志
| 日期 | 模块 | 内容 | 下次继续 |
|------|------|------|---------|
| 2026-04-30 | - | 教学方案制定 | Module 0 开始 |
| 2026-05-01 | Module 0 | 数据探索、OHLCV聚合代码、volume/maker-taker/截面vs时序概念 | Module 1: 相关性分析 |
| 2026-05-06 | Module 1A | 期望/方差/协方差推导、Pearson定义与\|ρ\|≤1证明、Spearman秩相关、截面IC | Module 1B: 假设检验 |
| 2026-05-06 | Module 1B | H₀/H₁框架、t统计量、两种SE、p-value、ICIR、多重比较与Bonferroni、自相关影响 | Module 1C: OLS回归 |
| 2026-05-07 | Module 1C | β=Cov/Var、β=ρ·σ_r/σ_f、标准化后β=ρ=IC、α推导、α与ε区别、方差分解、R²=ρ² | Module 1D: 时间序列基础 |
| 2026-05-07 | Module 1D | 平稳性、γ(k)和ACF ρ(k)、ACF=Pearson、Var(mean)自相关修正、ACF显著性±2/√T、Newey-West动机 | Module 2: 数据处理与因子构建 |
| 2026-05-07 | Module 2 | 简单/对数收益率、面板groupby、GroupBy对象/transform/apply、截面Winsorize、前向收益率、5个基础因子（动量/波动率/成交/Amihud/反转）、截面标准化（Z-score/Rank/MinMax） | Module 3: 因子评估体系 |
| 2026-05-08 | Module 3A | 截面IC vs 时序IC、groupby+apply算每日Rank IC、ICIR×√T(IID t-stat)、Newey-West修正（Bartlett权重、自协方差γ(k)）、scipy.stats.t.sf、完整calc_ic_stats函数 | Module 3B: IR与因子质量 |
| 2026-05-09 | Module 3B | 多期限前向收益率、IC衰减曲线（list-of-dicts→DataFrame模式）、半衰期推导(ln2/λ)与两种估算（np.polyfit拟合+直接查表）、mean_IC vs t_nw、iloc vs loc vs []索引、dict多key取值 | Module 3C: 分位数组合测试 |
| 2026-05-09 | Module 3C | IC局限性、pd.qcut分组、unstack/stack长宽转换、分位组合收益、多空价差、cumprod累计净值、年化Sharpe推导(mean/std×√N)、分组单调性、DataFrame df[]是列操作、完整calc_quantile_portfolio函数 | Module 3D: 换手率分析 |
| 2026-05-09 | Module 3D | 换手率定义(1-\|A∩B\|/\|A\|)、groupby+apply(set)提取成员集合、shift对齐相邻日期、apply(axis=1)逐行运算、unstack展开换手率、交易成本(taker 5e-4×2×换手率之和)、扣费后净Sharpe、IC衰减与换手率关系 | Module 4: 因子组合与策略构建 |
| 2026-05-10 | Module 4 | 因子合成（等权/IC/ICIR加权、combine_factors函数、前视偏差与定期更新）、反波动率仓位管理（calc_position、pd.qcut分组、1/vol加权、.loc赋值vs链式索引）、回测框架（backtest函数、cumprod累计净值、cummax回撤、Sharpe/Calmar、pd.concat vs pd.merge） | Module 5: 实战项目 |
| 2026-05-11 | Module 5 计划修订 | 三智能体并行审核研究计划：确认62变体无方向性因子、START_DATE改为2023-01（宇宙~195币种）、添加FDR多重检验校正、窗口步长改为比例制(WINDOW_STEP_RATIO=1/3, 解决98.6%重叠)、添加基准对比(buy-and-hold/随机因子/baseline)、添加Regime分段分析、添加风险管理规则(仓位≤5%/波动率≤2%/回撤熔断10%)、三阶段效率路线(数据探索→基础实现→优化提升)、代码模块化(utils.py+factor_lib.py) | Step 5.0: 数据探索 |

## Connections
- [[momentum-factor-research-plan]] — Module 5 的详细研究计划书
- [[MOC-Quantitative-Strategy]] — 因子研究整体知识地图
- [[MOC-Python]] — Python 编程知识地图
- [[MOC-Mathematics]] — 数学知识地图
