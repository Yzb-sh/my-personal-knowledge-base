---
id: "202604271510"
title: "OLTP vs OLAP"
created: "2026-04-27T15:10"
updated: "2026-05-12T22:00"
tags:
  - type/zettel
  - domain/sql
  - mastery/1-introduced
aliases: []
---
# OLTP vs OLAP

## Core Definition

数据库系统的两大工作负载类型。OLTP (Online Transaction Processing) 处理大量短小的读写事务；OLAP (Online Analytical Processing) 处理少量但扫描大量数据的复杂分析查询。

## My Understanding

OLTP 是"柜台"——每次处理一笔交易，快速读写一条记录，比如淘宝下单。OLAP 是"后台仓库"——一次性分析海量数据出报表，比如算全站月度销售趋势。量化研究中，交易系统本身是 OLTP，但策略研究（分析历史 L2 数据）是 OLAP。

## Why It Matters

理解 OLTP vs OLAP 是数据库选型的基础。面试问"为什么用 ClickHouse 不用 MySQL"，本质就是在问 OLTP 和 OLAP 的区别。

## Technical Details

| 维度 | OLTP | OLAP |
|------|------|------|
| 操作模式 | 大量单条 INSERT/UPDATE/SELECT | 少量大查询，全表或大范围扫描 |
| 每次读写量 | 几条到几百条记录 | 百万到数十亿条记录 |
| 存储方式 | 行存储 | 列存储 |
| 典型查询 | `SELECT * FROM users WHERE id = 42` | `SELECT avg(price) FROM ticks WHERE date BETWEEN ... GROUP BY code` |
| 延迟要求 | 毫秒级 | 秒到分钟级可接受 |
| 代表数据库 | MySQL, PostgreSQL, Oracle | ClickHouse, Apache Doris, Snowflake |
| 数据量 | GB 到 TB | TB 到 PB |

**HTAP（混合事务/分析处理）**：部分新数据库试图同时支持两者（如 TiDB, OceanBase），但通常在某一方面有所妥协。

## Application Example

量化研究中的两种场景：

- **OLTP 场景**：交易系统记录每笔成交，实时写入，需要 ACID 保证（MySQL / 交易所内部数据库）
- **OLAP 场景**：研究员分析一年 L2 数据计算因子 IC，需要扫描数十亿条记录（ClickHouse）

## Common Misconceptions

1. "MySQL 也能分析大数据" -> 能，但比列存储数据库慢几十倍
2. "OLTP 和 OLAP 互斥" -> 不是，一个系统可以同时有 OLTP 和 OLAP 需求，但通常用不同数据库

## Connections
- [[Row Storage vs Column Storage]] -- OLTP 用行存储，OLAP 用列存储
- [[MongoDB vs MySQL vs ClickHouse]] -- MySQL 是 OLTP，ClickHouse 是 OLAP
- [[L2 Market Data Storage Strategy]] -- L2 数据分析属于 OLAP 场景

## References
