---
id: "202604271500"
title: "Row Storage vs Column Storage"
created: "2026-04-27T15:00"
updated: "2026-05-12T22:00"
tags:
  - type/zettel
  - domain/sql
  - mastery/1-introduced
aliases: []
---
# Row Storage vs Column Storage

## Core Definition

数据在磁盘上的两种物理组织方式。行存储（Row-oriented）按记录逐行连续存放；列存储（Column-oriented）按列将同类数据连续存放。

## My Understanding

行存储就像 Excel 一行一行写入磁盘，一条记录的所有字段存在一起，适合"读一条完整记录"的场景（如查某个用户的全部信息）。列存储把每一列的数据单独打包，适合"对某几列做聚合计算"的场景（如算所有股票某天的平均价格）。量化研究中的 L2 数据分析几乎都是列存储场景。

## Why It Matters

存储方式直接决定查询性能，选错会导致查询慢几十倍甚至上百倍。面试中"为什么用 ClickHouse 存 L2 数据"的核心答案就是列存储。

## Technical Details

**行存储**
- 一条记录的所有字段连续存储在一起
- 代表：MySQL (InnoDB), PostgreSQL, MongoDB (BSON)
- 优势：点查询快（读一条完整记录只需一次 I/O），单行插入/更新高效
- 劣势：分析查询慢（只需几列但必须读取所有列的数据），压缩率低（不同类型数据混在一起）

**列存储**
- 同一列的所有值连续存储在一起
- 代表：ClickHouse, Apache Parquet, Apache ORC
- 优势：
  - 分析查询快：只读需要的列，跳过无关列
  - 压缩率高：同类型数据连续存储，编码效率高（如整数列可用 delta encoding）
  - 向量化执行：对一列数据批量做 SIMD 运算
- 劣势：单行插入/更新慢（需要定位到多个列块），点查询不占优

**面试陷阱：列存储与查询条件不矛盾**
- "按 tradedate 查询是否与列存储矛盾？" -> 不矛盾
- 列存储解决的是**"读哪些列"**的问题
- 按 tradedate 查询是**"筛选哪些行"**的问题
- 两者完全正交，实际中 ClickHouse 配合分区（`PARTITION BY toYYYYMMDD(timestamp)`）实现按日期的高效行筛选

## Application Example

L2 逐笔数据：每天 5000 万条记录、50 个字段。查询 `SELECT avg(price) FROM data WHERE tradedate = '2026-04-27'`：

- **行存储**：必须读取所有 50 列的数据，I/O 量 = 5000万 x 50列 x 平均字段大小
- **列存储**：只读取 price 和 tradedate 两列，I/O 量减少约 96%

## Common Misconceptions

1. "列存储就是按列建索引" -> 不是索引，是物理存储方式不同
2. "列存储不能按行查询" -> 可以，只是效率不如行存储
3. "列存储和分区是同一回事" -> 不是，列存储管列，分区管行，两个独立维度

## Connections
- [[OLTP vs OLAP]] -- 行存储对应 OLTP，列存储对应 OLAP
- [[MongoDB vs MySQL vs ClickHouse]] -- 三种数据库各自的存储方式
- [[Parquet File Format]] -- Parquet 是列存储文件格式

## References
