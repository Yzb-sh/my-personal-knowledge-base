---
id: "202605101001"
title: "Inverse Volatility Position Sizing"
created: "2026-05-10T10:01"
updated: "2026-05-10T10:01"
tags:
  - type/zettel
  - domain/quant
  - domain/python
  - mastery/1-introduced
aliases: []
---
# Inverse Volatility Position Sizing

## Core Definition
反波动率加权是一种仓位管理方法：每个资产的仓位权重与其波动率成反比（$w_i \propto 1/\sigma_i$），使得每个资产对组合风险的贡献大致相等。常用于多空策略的组内权重分配。

## My Understanding
如果等权分配，波动率高的币种对组合风险的贡献远大于波动率低的币种。反波动率加权让高波动率的币自动获得更小的仓位，这样每个币对组合风险的贡献大致相等。完整的仓位计算分四步：先用综合因子排序分组，然后算 1/volatility 作为初始权重，再把中间组的权重清零，最后在多头组和空头组内分别归一化（使多头权重之和 = 0.5，空头 = -0.5）。

## Why It Matters
在加密货币市场，不同币种的波动率差异极大（BTC vs 小市值 altcoin）。如果不做波动率调整，高波动币会主导组合风险，策略表现完全取决于少数高波动资产。反波动率加权使风险来源分散化。

## Technical Details

**仓位计算函数 — `calc_position`**
```python
def calc_position(df, composite_col, vol_col, n_groups=5):
    # Step 1: 按综合因子值截面分组
    df['com_group'] = df.groupby('date')[composite_col].transform(
        lambda x: pd.qcut(x, n_groups, labels=range(1, n_groups + 1))
    )
    # Step 2: 计算初始反波动率权重，中间组清零
    df['position'] = 1 / df[vol_col]
    mask = df['com_group'].isin(range(2, n_groups))
    df.loc[mask, 'position'] = 0
    # Step 3: 多头组（第 n_groups 组）和空头组（第 1 组）内归一化
    mask = df['com_group'].isin([1, n_groups])
    df.loc[mask, 'position'] = df.loc[mask].groupby(['date', 'com_group'])['position'].transform(
        lambda x: x / x.sum() * 0.5
    )
    # Step 4: 空头组取负
    mask = (df['com_group'] == 1)
    df.loc[mask, 'position'] = -df.loc[mask, 'position']
    return df
```

**四步流程**

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | `pd.qcut` 分组 | 每只币分到 1~5 组 |
| 2 | `1/vol` 初始权重，中间组清零 | 第 1、5 组有权重，其余为 0 |
| 3 | 组内归一化 `x/x.sum()*0.5` | 每组权重之和 = 0.5 |
| 4 | 空头取负 | 第 1 组权重为负，第 5 组为正 |

**多空组合的仓位分配**
- 多头组（第 5 组）：权重为正，总和 = +0.5
- 空头组（第 1 组）：权重为负，总和 = -0.5
- 中间组（第 2、3、4 组）：权重 = 0，不持仓
- 多空组合净暴露 = 0（market neutral）

## Application Example
458 只加密货币的综合因子排序后分 5 组。第 5 组 90 只币做多，第 1 组 90 只币做空。BTC 波动率 2%，某小市值币波动率 8%，则 BTC 的仓位是小市值币的 4 倍，两者对组合风险的贡献相等。

## Common Misconceptions
- `.isin()` 语法错误（本次会话犯 3+ 次）：正确写法是 `df['col'].isin([1,2,3])`——有**点号**、有**括号**、有**方括号**。常见错误写法：`isin[2,3,4]`、`isin(2,3,4)`、`df['col'] isin [2,3,4]`
- 链式索引赋值不生效：`df[mask]['col'] = value` 是链式索引，Pandas 不保证生效。正确写法：`df.loc[mask, 'col'] = value`
- lambda 中不能使用 if/elif/else 语句块：lambda 只能写单个表达式，条件判断用三元表达式 `x if cond else y`，复杂逻辑应该用 `def` 定义函数
- `=` vs `==`（本次会话犯 4 次）：`=` 是赋值，`==` 是比较。在 `if` 语句中必须用 `==`。建议规则：写 if 判断时先写 `==` 再填两边
- 布尔 mask 用 `df[df['col']==1]`（返回 DataFrame）而非 `df['col']==1`（返回 True/False Series）。`.loc` 需要后者
- `df.loc[mask, 'position'] = -df.loc[mask, 'position']` 是正确的取反写法

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于组合构建和风险管理板块
- [[MOC-Python]] -- Pandas .loc 赋值、groupby transform、布尔索引
- [[Factor Combination Methods]] -- 合成综合因子是仓位计算的前置步骤
- [[Quantile Portfolio Testing]] -- 仓位分组逻辑与分位数分组一脉相承
- [[Turnover Analysis and Transaction Costs]] -- 仓位变化产生换手和交易成本
- [[Pandas GroupBy Transform and Apply]] -- groupby + transform 是组内归一化的基础
- [[Pandas Series and DataFrame]] -- .loc 索引和布尔 mask 的基础

## References
- 因子分析教学 Module 4B（2026-05-09/10 会话）
