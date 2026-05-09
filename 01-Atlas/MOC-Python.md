---
id: "moc-20260427-python"
title: "MOC-Python"
created: "2026-04-27"
updated: "2026-05-09"
tags:
  - type/structure
---
# MOC-Python

量化研究相关的 Python 编程知识体系。

## Fundamentals (基础)
- [[...]] -- Data Types and Variables (数据类型与变量)
- [[...]] -- Control Flow (控制流：if/else, loops, comprehensions)
- [[...]] -- Functions and Scope (函数与作用域)
- [[...]] -- Classes and OOP (类与面向对象)
- [[...]] -- Error Handling (错误处理：try/except)
- [[...]] -- File I/O (文件读写)
- [[...]] -- Virtual Environments (虚拟环境与包管理)

## NumPy (数值计算)
- [[...]] -- NumPy Arrays and dtypes (数组与数据类型)
- [[...]] -- NumPy Indexing and Slicing (索引、切片、布尔掩码)
- [[...]] -- NumPy Broadcasting (广播机制)
- [[...]] -- NumPy Linear Algebra linalg (线性代数模块)
- [[...]] -- NumPy Random Number Generation (随机数生成)

## Pandas (数据分析)
- [[Pandas Series and DataFrame]] -- Pandas Series 与 DataFrame：核心数据结构与基础操作
- [[...]] -- Pandas Indexing loc iloc (索引：loc, iloc, at)
- [[Pandas GroupBy Transform and Apply]] -- Pandas GroupBy Operations (分组操作：transform vs apply)
- [[...]] -- Pandas Merge Join Concat (合并：Merge, Join, Concat)
- [[...]] -- Pandas Time Series Handling (时间序列处理)
- [[Factor Construction with Rolling Windows]] -- Pandas Rolling and Expanding Windows (滚动与扩展窗口：因子构建的统一模式)
- [[...]] -- Pandas Performance Tips (性能优化：向量化、避免循环)

## Data Formats (数据格式)
- [[Parquet File Format]] -- Parquet 列式文件格式的原理和优势
- [[Processing Parquet with Python]] -- Python 读写和处理 Parquet 文件的完整方法

## Visualization (可视化)
- [[...]] -- Matplotlib Fundamentals (Matplotlib 基础)
- [[...]] -- Seaborn for Statistical Plots (Seaborn 统计图表)
- [[...]] -- Plotly for Interactive Charts (Plotly 交互图表)

## Quantitative Libraries (量化库)
- [[...]] -- SciPy Statistical Functions (SciPy 统计函数)
- [[...]] -- Statsmodels Regression and Time Series (Statsmodels 回归与时间序列)
- [[...]] -- scikit-learn Cross-Validation Regularization (交叉验证与正则化)
- [[...]] -- Backtesting Frameworks (回测框架：backtrader, zipline, vectorbt)

## Cross-Domain Connections
- [[Processing Parquet with Python]] (Python↔量化) -- 用Python处理L2逐笔Parquet数据
- [[L2 Market Data Storage Strategy]] (Python↔量化) -- Parquet存储策略服务于量化研究
- [[IC Decay and Half-Life Estimation]] (Python↔量化) -- np.polyfit线性拟合实现半衰期估算
- [[Quantile Portfolio Testing]] (Python↔量化) -- pd.qcut分位数分组、unstack宽格式转换、cumprod累计净值

## See Also
- [[MOC-Home]] -- 返回主索引
- [[MOC-Mathematics]] -- 数学概念
- [[MOC-SQL]] -- 数据查询
- [[MOC-Quantitative-Strategy]] -- 策略实现

## Gaps & Next Steps
- [ ] 确定最需要加强的 Python 领域
- [ ] 收集常用代码片段到 T-Code-Snippet 笔记
