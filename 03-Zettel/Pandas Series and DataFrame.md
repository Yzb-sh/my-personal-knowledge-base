---
id: "202604281530"
title: "Pandas Series and DataFrame"
created: "2026-04-28T15:30"
updated: "2026-05-09T15:00"
tags:
  - type/zettel
  - domain/python
  - mastery/1-introduced
aliases: []
---
# Pandas Series and DataFrame

## Core Definition
Pandas 的两种核心数据结构。DataFrame 是二维表格（有行索引和列名），Series 是一维数组带索引，可以理解为"只有一列的 DataFrame"。

## My Understanding
DataFrame 从字典创建时，key 自动变成列名，value 变成列数据，所有 value 长度必须一致。行索引默认是 0,1,2,...，可以通过 `index` 参数指定；列名可以通过 `columns` 参数指定或重排。Series 是只有一列的 DataFrame，或者说一维数组带索引。`idxmax()` 返回最大值的索引，`max()` 返回最大值本身。多个方法可以链式调用，一行搞定整个计算流程。

## Why It Matters
DataFrame 和 Series 是所有 Pandas 操作的基础。量化研究中，股票面板数据天然适合用 DataFrame 存储（行=日期，列=股票），而计算结果（如每只股票的波动率）通常是一个 Series。

## Technical Details
- `pd.DataFrame(dict)` — 字典创建，key→列名，value→列数据
- `pd.DataFrame(data, index=dates)` — 指定行索引
- `pd.DataFrame(data, columns=['A', 'B'])` — 指定/筛选列
- `.T` — 转置属性（不是方法，不加括号）
- `df.pct_change()` — 对整个 DataFrame 逐列计算变化率，返回 DataFrame
- `df.std()` — 对 DataFrame 返回每列标准差（Series）
- `series.idxmax()` — 返回最大值对应的索引
- `series.max()` — 返回最大值本身
- `.iloc[i]` — 按位置索引，永远取第 i 个元素，不管 index label 是什么
- `.loc[i]` — 按 label 索引，找 index==i 的行
- `s[i]` — 行为模糊，先尝试 label 索引，找不到时退回位置索引，不推荐使用
- 过滤后的 DataFrame/Series index 不连续，用 `[0]` 可能找不到 label 0 → 用 `.iloc[0]`

## Application Example
从股票日线数据计算日收益率并找出波动最大的股票：
```python
df = pd.DataFrame(data, index=dates)
max_code = df.pct_change().fillna(0).std().idxmax()
```

## Common Misconceptions
- 字典创建 DataFrame 时，key 变成的是**列名**而非行索引
- `.T` 是属性不是方法，写成 `.T()` 会报错
- `pct_change()` 默认 axis=0，是在**每列内部**逐行计算变化率，不是跨列操作
- `idxmax()` 对 Series 调用时返回行标签，对 DataFrame 调用时默认返回每列最大值所在的行索引
- `df[0]` 是按列名查找（找叫 `0` 的列），不是取第一行 → 取第一行的某列用 `df['col'].iloc[0]`
- 过滤 DataFrame 后 index 保留原值（如 [0, 3, 7]），此时 `.loc[0]` 找 label 0 能找到，但 `.loc[2]` 会 KeyError（label 2 已被过滤掉）
- `s[i]` 对 Series 先当 label 找，找不到时退回 position → 行为不可预测，始终优先用 `.iloc[i]` 或 `.loc[i]` 明确意图

## Connections
- [[MOC-Python]] -- 属于 Pandas 数据分析板块
- [[Processing Parquet with Python]] -- Parquet 文件读入后的数据结构就是 DataFrame
- [[Parquet File Format]] -- Parquet 的列式存储与 DataFrame 的列操作天然契合

## References
- Pandas 官方文档：DataFrame, Series
