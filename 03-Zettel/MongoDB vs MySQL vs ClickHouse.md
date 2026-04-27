---
id: "202604271540"
title: "MongoDB vs MySQL vs ClickHouse"
created: "2026-04-27T15:40"
updated: "2026-04-27T15:40"
tags:
  - type/zettel
  - domain/sql
  - mastery/1-introduced
aliases: []
---
# MongoDB vs MySQL vs ClickHouse

## Core Definition

三种代表不同设计理念的数据库系统。MySQL 是关系型数据库（行存储，OLTP），MongoDB 是文档型 NoSQL 数据库（行存储，灵活 Schema），ClickHouse 是列式分析数据库（列存储，OLAP）。面试问"跟 MongoDB/MySQL 有什么区别"，核心是考你理解不同数据库的设计取舍。

## My Understanding

这三种数据库不是"谁比谁好"的关系，而是各自针对不同场景优化的工具。MySQL 适合需要事务保证的业务系统，MongoDB 适合 Schema 不固定的快速开发，ClickHouse 适合海量数据分析。L2 数据分析是典型的分析场景，所以选 ClickHouse。面试中说"按列存取比较高效"是对的，但要说清楚为什么——因为分析查询只需要几列，列存储可以跳过无关列，减少 I/O。

## Why It Matters

这是面试高频问题。理解三种数据库的本质区别，才能在面试中有逻辑地回答"为什么选 ClickHouse"。

## Technical Details

**全面对比**

| 维度 | MySQL | MongoDB | ClickHouse |
|------|-------|---------|------------|
| 类型 | 关系型 (RDBMS) | 文档型 (NoSQL) | 列式分析 (OLAP) |
| 存储方式 | 行存储 (InnoDB) | 行存储 (BSON) | 列存储 |
| 查询语言 | SQL | MongoDB Query (MQL) | SQL |
| Schema | 固定表结构 | 灵活文档结构 | 固定表结构 |
| 事务支持 | 强 (ACID) | 4.0+ 支持多文档事务 | 有限（不适合 OLTP） |
| 写入模式 | 单条高效 | 单条高效 | 批量高效 |
| 分析性能 | 慢（全行读取） | 慢（全文档读取） | 极快（只读需要的列） |
| 压缩率 | 一般 | 一般（BSON 比 JSON 紧凑） | 高（列式编码） |
| 分区能力 | 范围/列表/哈希分区 | 分片 (Sharding) | 分区 (PARTITION BY) |
| 适用场景 | 业务系统、交易记录 | 日志、内容管理、原型 | 数据分析、时序、报表 |
| 适合L2数据 | 不适合 | 不适合 | 适合 |

**面试回答模板**

"我们用 ClickHouse 存储 L2 数据，主要原因是：
1. L2 数据量大（TB 级），分析查询只涉及部分字段，ClickHouse 的列存储只读需要的列，大幅减少 I/O
2. 我们按交易日期分区（PARTITION BY toYYYYMMDD），查询特定日期时通过分区裁剪跳过无关数据
3. 列存储压缩率高，存储成本比行存储低很多
4. 支持标准 SQL，学习成本低

相比之下，MySQL 是行存储，分析查询需要读取全部字段，在 TB 级数据量下性能不可接受。MongoDB 虽然灵活，但也是行存储，同样不适合大规模分析。"

## Application Example

同一条查询在不同数据库中的表现差异：

```sql
SELECT code, avg(price), sum(volume)
FROM l2_ticks
WHERE trade_time >= '2026-04-27'
  AND trade_time < '2026-04-28'
GROUP BY code;
```

假设 50 亿条记录、50 个字段、每天 5000 万条：
- **MySQL**：需读取所有 50 列数据（行存储），全表扫描或索引扫描，预计耗时：分钟到小时级
- **MongoDB**：类似问题，BSON 文档需完整加载，分析性能差
- **ClickHouse**：只读 3 列（code, price, volume），加上分区裁剪只扫当天分区，预计耗时：毫秒到秒级

## Common Misconceptions

1. "ClickHouse 可以替代 MySQL" -> 不能，ClickHouse 不适合 OLTP（高频单条读写、事务）
2. "MongoDB 比 MySQL 快" -> 不一定，取决于场景。分析查询都不快，因为都是行存储
3. "用了 ClickHouse 就不需要考虑分区了" -> 错误，分区设计直接影响查询性能

## Connections
- [[Row Storage vs Column Storage]] -- MySQL/MongoDB 是行存储，ClickHouse 是列存储
- [[OLTP vs OLAP]] -- MySQL 是 OLTP，ClickHouse 是 OLAP
- [[Database Partitioning]] -- ClickHouse 的分区策略
- [[Time-Series Database]] -- ClickHouse 可作为时序数据库使用
- [[L2 Market Data Storage Strategy]] -- 为什么 L2 数据选 ClickHouse

## References
