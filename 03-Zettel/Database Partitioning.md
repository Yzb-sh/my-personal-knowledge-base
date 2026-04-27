---
id: "202604271520"
title: "Database Partitioning"
created: "2026-04-27T15:20"
updated: "2026-04-27T15:20"
tags:
  - type/zettel
  - domain/sql
  - mastery/1-introduced
aliases: []
---
# Database Partitioning

## Core Definition

将一张大表按照特定规则拆分成多个物理存储单元的技术。分区（Partitioning）在单个数据库实例内拆分；分片（Sharding）跨多个数据库实例分布。两者可以独立使用，也可以组合使用。

## My Understanding

分区就像把一本厚书按章节分成多册——查询时直接翻到目标分册，不用从头到尾翻。分片就像把书复印多份放在不同图书馆——分散访问压力。L2 数据按日期分区是最自然的选择，查询特定日期时直接跳过其他分区。

## Why It Matters

面试直接问"知不知道分区分表"。对于 TB 级 L2 数据，没有分区策略意味着每次查询都要全表扫描，完全不可用。

## Technical Details

**分区 (Partitioning)**
- 在单个数据库实例内，将一张逻辑表拆成多个物理存储单元
- 常见分区策略：
  - **范围分区** (Range)：按日期、按 ID 范围。最常用
  - **列表分区** (List)：按枚举值（如按交易所代码）
  - **哈希分区** (Hash)：按某列的哈希值均匀分布
- **分区裁剪 (Partition Pruning)**：查询时数据库自动跳过不相关的分区，大幅减少 I/O

**ClickHouse 分区语法**
```sql
CREATE TABLE l2_ticks (
    trade_time DateTime,
    code String,
    price Float64,
    volume UInt64
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(trade_time)
ORDER BY (code, trade_time);
```

**分片 (Sharding)**
- 将数据分布到多个数据库实例/服务器上
- 解决单机存储和计算瓶颈
- ClickHouse 支持分布式表（Distributed引擎）+ 分片集群
- 权衡：增加系统复杂度，需要处理分布式一致性问题

**分区 vs 分片的区别**
| 维度 | 分区 | 分片 |
|------|------|------|
| 范围 | 单个数据库实例内 | 跨多个实例/服务器 |
| 对应用透明 | 是（应用看到的是一张表） | 部分透明（取决于中间件） |
| 主要目的 | 查询性能（减少扫描量） | 容量和并发（水平扩展） |
| 复杂度 | 低 | 高 |

## Application Example

L2 逐笔数据按天分区：
```sql
-- 查询某天的数据，自动裁剪其他分区
SELECT code, avg(price), sum(volume)
FROM l2_ticks
WHERE trade_time >= '2026-04-27 00:00:00'
  AND trade_time < '2026-04-28 00:00:00'
GROUP BY code;
-- 只扫描 2026-04-27 这一个分区，跳过其他所有天
```

**为什么按 tradedate 查而不是按 code 查？**
L2 数据每天每个股票都有数据。如果按 code 分区，查一只股票全年的数据只扫一个分区，但查一天所有股票的数据要扫所有分区。量化研究更多是"查某天/某段时间的全市场数据做截面分析"，所以按日期分区更合理。

## Common Misconceptions

1. "分区就是分表" -> 不完全相同。分区是一张逻辑表内的物理拆分（对应用透明），分表是创建多张独立的表（需要应用层处理路由）
2. "分了区就不需要索引了" -> 分区和索引是互补的，不是替代关系
3. "按列存储就不需要分区了" -> 列存储解决读列效率，分区解决读行范围效率，两个维度

## Connections
- [[Row Storage vs Column Storage]] -- 分区和列存储是两个独立维度
- [[Time-Series Database]] -- 时序数据库通常自动按时间分区
- [[MongoDB vs MySQL vs ClickHouse]] -- 各数据库的分区能力不同
- [[L2 Market Data Storage Strategy]] -- L2 数据按日期分区的具体方案

## References
