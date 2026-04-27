---
id: "moc-20260427-sql"
title: "MOC-SQL"
created: "2026-04-27"
updated: "2026-04-27"
tags:
  - type/structure
---
# MOC-SQL

量化数据查询相关的 SQL 知识体系。

## Database Fundamentals (数据库基础)
- [[Row Storage vs Column Storage]] -- 行存储与列存储的原理和适用场景
- [[OLTP vs OLAP]] -- 在线事务处理 vs 在线分析处理
- [[Database Partitioning]] -- 分区与分片的原理和策略
- [[Time-Series Database]] -- 时序数据库的概念和选型
- [[MongoDB vs MySQL vs ClickHouse]] -- 三种数据库的全面对比

## Fundamentals (基础)
- [[...]] -- SELECT, WHERE, ORDER BY
- [[...]] -- Aggregation GROUP BY HAVING (聚合：GROUP BY, HAVING)
- [[...]] -- Joins INNER LEFT RIGHT FULL CROSS (连接：各类 JOIN)
- [[...]] -- Subqueries and CTEs (子查询与公用表表达式)

## Intermediate (进阶)
- [[...]] -- Window Functions ROW_NUMBER RANK LAG LEAD (窗口函数)
- [[...]] -- Date and Time Functions (日期时间函数)
- [[...]] -- CASE WHEN Conditional Logic (条件逻辑)
- [[...]] -- Query Optimization EXPLAIN (查询优化与执行计划)

## Advanced (高级)
- [[...]] -- Recursive CTEs (递归 CTE)
- [[...]] -- Pivot and Unpivot (行列转换)
- [[...]] -- Materialized Views (物化视图)
- [[...]] -- Indexing Strategies (索引策略)

## Quantitative Data Patterns (量化数据模式)
- [[L2 Market Data Storage Strategy]] -- L2行情数据的存储架构设计
- [[...]] -- OHLCV Bar Construction (K线数据构建)
- [[...]] -- Time-Series Analytics Patterns (时序分析模式)
- [[...]] -- Cross-Sectional Factor Queries (截面因子查询)

## Cross-Domain Connections
- [[L2 Market Data Storage Strategy]] (SQL↔量化) -- 数据库选型服务于量化数据存储
- [[Parquet File Format]] (SQL↔Python) -- 列存储在文件层面的实现

## See Also
- [[MOC-Home]] -- 返回主索引
- [[MOC-Python]] -- Python 数据分析
- [[MOC-Quantitative-Strategy]] -- 策略中的数据查询

## Gaps & Next Steps
- [ ] 确定工作中最常用的 SQL 场景
- [ ] 收集常用查询模板
