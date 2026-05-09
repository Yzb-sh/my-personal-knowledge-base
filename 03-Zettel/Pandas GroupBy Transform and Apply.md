---
id: "202605072010"
title: "Pandas GroupBy Transform and Apply"
created: "2026-05-07T20:10"
updated: "2026-05-08T21:00"
tags:
  - type/zettel
  - domain/python
  - mastery/2-familiar
aliases: []
---
# Pandas GroupBy Transform and Apply

## Core Definition
GroupBy 对象是 Pandas 中分组操作的懒执行中间状态：它记录了分组规则但尚未进行任何计算。transform 和 apply 是 GroupBy 上两种核心操作方法，transform 要求返回与 group 等长的结果，apply 没有形状限制。

## My Understanding
GroupBy 对象是懒执行的中间状态，记住了分组规则但没有做任何计算。当你调用 .transform()、.mean()、.apply() 时，Pandas 才会在每个子 DataFrame 上执行操作，然后把结果拼回来。transform 必须返回跟 group 一样长的结果（或者一个标量广播到整组），apply 更通用，没有返回形状的限制。做因子构建时用 transform，因为需要返回等长的结果直接赋值回原表。

## Why It Matters
量化面板数据（date × symbol）的几乎所有操作都依赖 groupby：收益率计算按 symbol 分组避免跨币种串数据，截面标准化按 date 分组做横向比较。理解 transform vs apply 的区别是写出正确因子计算代码的关键。

## Technical Details

**GroupBy 对象**
- `df.groupby('symbol')` 返回 GroupBy 对象，此时什么都不计算
- `df.groupby('symbol')['close']` 返回 SeriesGroupBy，在每个 group 内取 close 列
- 后续操作（mean/sum/std/transform/apply）在每个 group 内分别执行，结果拼回

**聚合 vs 变换**
- 聚合（mean/sum/std）: 每个 group 返回一个值，结果长度 = group 数量
- 变换（transform）: 每个 group 返回等长结果，结果长度 = 原始数据长度

**transform vs apply**
- `transform(func)`: func 必须返回与 group 等长的结果，或返回标量（自动广播）
- `apply(func)`: func 可以返回任意形状的结果
- transform 语义更明确，性能可能更好（Pandas 知道输出形状）
- 当需要"分组变换后赋值回原表"时，优先用 transform

**面板数据常见模式**
```python
# 时序操作：按 symbol 分组（用 transform 赋值回原表）
df.groupby('symbol')['close'].pct_change()
df.groupby('symbol')['col'].transform(lambda x: x.rolling(N).op())

# 截面操作：按 date 分组（用 transform 赋值回原表）
df.groupby('date')['col'].transform(lambda x: (x - x.mean()) / x.std())

# 截面聚合：按 date 分组（用 apply 返回每组一个值）
df.groupby('date')[['factor', 'return']].apply(
    lambda x: x['factor'].corr(x['return'], method='spearman')
)
```

**Series.groupby() 注意事项**
- `df['close'].groupby('symbol')` 会报错，因为 Series 上没有 'symbol' 列
- 正确做法: `df.groupby('symbol')['close']`（先 groupby 再取列）

## Application Example
截面 Winsorize：按 date 分组，在每个 group 内计算分位数并截断：
```python
df['return_1d'] = df.groupby('date')['return_1d'].transform(
    lambda x: x.clip(x.quantile(0.01), x.quantile(0.99))
)
```

## Common Misconceptions
- 在 Series 上用 groupby('column_name')：Series 没有列名，应该用 df.groupby() 先分组再取列
- 直接用 df.groupby('symbol')['close'].rolling(20).sum() 赋值给列：返回 MultiIndex，无法对齐
- 混淆聚合和变换：mean() 返回聚合结果（每个 group 一个值），transform(lambda x: x.mean()) 返回变换结果（每个原始行一个值）

## Connections
- [[MOC-Python]] -- 属于 Pandas 数据分析板块
- [[Pandas Series and DataFrame]] -- GroupBy 操作的基础是 DataFrame 和 Series
- [[Simple and Log Returns]] -- 面板数据收益率计算需要 groupby('symbol')
- [[Factor Construction with Rolling Windows]] -- 因子构建的统一代码模式基于 groupby+transform
- [[Cross-Sectional vs Time-Series Data]] -- groupby 的分组维度决定了操作的时序/截面性质

## References
- 因子分析教学 Module 2A（2026-05-07 会话）
- 因子分析教学 Module 3A（2026-05-08 会话）— apply 的 IC 计算应用
- Pandas 官方文档: GroupBy, transform, apply
