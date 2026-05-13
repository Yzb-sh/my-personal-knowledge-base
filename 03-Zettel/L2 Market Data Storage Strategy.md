---
id: "202604271550"
title: "L2 Market Data Storage Strategy"
created: "2026-04-27T15:50"
updated: "2026-05-12T22:00"
tags:
  - type/zettel
  - domain/quant
  - mastery/2-familiar
aliases: []
---
# L2 Market Data Storage Strategy

## Core Definition

Level 2 (L2) 行情数据（逐笔委托、逐笔成交、盘口快照）的存储架构设计。由于数据量极大（TB 级）且查询模式固定（按日期范围 + 少量字段聚合），需要选择合适的数据库和存储策略。

## My Understanding

L2 数据是量化研究的基础设施。面试中被问到 L2 数据存储，其实是在考察你：（1）是否理解数据规模，（2）是否理解为什么用特定的技术方案，（3）能不能从原理层面解释技术选型。我的实际经验是 L2 数据有几个 TB，用 ClickHouse 按列存储和按日期分区来管理。但之前我只知其然不知其所以然，现在补上底层原理。

## Why It Matters

存储方案选错，日常研究效率会受严重影响。面试中这是高频考点，也是实际工作中每天都要面对的基础设施问题。

## Technical Details

**L2 数据特征**
- 数据量：数 TB（全市场 L2 逐笔数据）
- 每天新增：数十 GB，数千万到数亿条记录
- 写入模式：批量导入历史数据，或盘中追加写入；几乎不更新、不删除
- 典型字段：trade_time, code, price, volume, turnover, order_type, bs_flag 等

**查询模式**
1. 截面查询（最常见）：查某天/某段时间全市场数据 -> 按 tradedate 查询
2. 时序查询：查某只股票一段时间走势 -> 按 code + 时间范围
3. 聚合分析：因子计算、统计指标 -> 对少量列做聚合

**为什么按 tradedate 查而不是按 code 查？**
- 量化研究多为截面分析（某天全市场横截面的因子暴露、收益等）
- 按日期分区后，查一天全市场数据只扫一个分区
- 如果按 code 分区，截面查询要扫所有分区

**推荐存储架构**

| 层级 | 技术 | 用途 |
|------|------|------|
| 历史数据存储 | ClickHouse | TB 级分析查询 |
| 文件交换格式 | Parquet | 数据导出、跨系统传输 |
| 本地分析 | Pandas/Polars + Parquet | 单机研究 |

**ClickHouse 建表示例**
```sql
CREATE TABLE l2_ticks (
    trade_time DateTime64(3),
    trade_date Date MATERIALIZED toDate(trade_time),
    code String,
    price Float64,
    volume UInt64,
    turnover Float64,
    order_type String,
    bs_flag String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(trade_time)
ORDER BY (trade_date, code, trade_time)
TTL trade_date + INTERVAL 3 YEAR;
```

**Parquet 分区存储示例**
```
L2_data/
├── trade_date=2026-04-25/
│   ├── part-0.parquet
│   └── part-1.parquet
├── trade_date=2026-04-26/
│   └── part-0.parquet
└── trade_date=2026-04-27/
    └── part-0.parquet
```

## Application Example

面试回答 L2 数据相关问题时的完整话术：

1. "L2 逐笔数据大概有几个 TB，每天新增数十 GB"
2. "用 ClickHouse 存储，因为是列存储，分析查询只读需要的字段"
3. "按交易日期分区，查询时通过分区裁剪跳过无关数据"
4. "为什么不按股票代码分区？因为量化研究更多是截面分析——查某天全市场数据，按日期分区更合理"
5. "ClickHouse 不是严格的时序数据库，但列存储 + 时间分区完全满足 L2 数据场景"

## Common Misconceptions

1. "L2 数据只能用 ClickHouse" -> 不是，Parquet + 本地分析也可行（数据量不是特别大时）
2. "按 code 查就必须按 code 分区" -> 二级索引或排序键（ORDER BY）也能优化按 code 查询，不必依赖分区
3. "TB 级数据就必须分片" -> 不一定，单机 ClickHouse 配足够磁盘可以管理 TB 级数据

## Connections
- [[Row Storage vs Column Storage]] -- 列存储是 ClickHouse 高效的根本原因
- [[Database Partitioning]] -- 按日期分区是 L2 数据查询性能的关键
- [[MongoDB vs MySQL vs ClickHouse]] -- 为什么选 ClickHouse 而不是其他数据库
- [[Parquet File Format]] -- Parquet 作为 L2 数据的文件交换格式
- [[Processing Parquet with Python]] -- 用 Python 处理 L2 Parquet 数据

## References
