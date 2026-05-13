---
id: "202604271530"
title: "Time-Series Database"
created: "2026-04-27T15:30"
updated: "2026-05-12T22:00"
tags:
  - type/zettel
  - domain/sql
  - mastery/1-introduced
aliases: []
---
# Time-Series Database

## Core Definition

专门为时间序列数据（每条记录带有时间戳、按时间顺序追加写入的数据）优化的数据库系统。核心特点是自动按时间分区、高效时间范围查询、内置时序聚合函数和数据生命周期管理。

## My Understanding

时序数据库就是专门为"带时间戳的数据流"设计的数据库。股票行情、服务器监控、IoT 传感器数据都是典型时序数据。面试官问"知不知道什么是时序数据库"，是想知道你是否理解 L2 数据的时序特征，以及为什么需要专门的存储方案。

## Why It Matters

L2 逐笔数据是典型的高频时序数据。理解时序数据库有助于理解为什么 ClickHouse 在这个场景下表现优异。

## Technical Details

**时序数据特征**
- 每条记录带时间戳
- 追加写入为主（INSERT），极少更新/删除
- 查询模式：按时间范围查询、时间聚合（分钟/小时/天）
- 数据量大且持续增长
- 数据有生命周期（热数据 vs 冷数据）

**专用时序数据库**
| 数据库 | 特点 |
|--------|------|
| InfluxDB | 专用 TSDB，类 SQL 查询语言（Flux/InfluxQL） |
| TimescaleDB | 基于 PostgreSQL 的 TSDB 扩展，兼容 SQL |
| QuestDB | 高性能开源 TSDB，SQL 接口 |
| OpenTSDB | 基于 HBase，适合超大规模 |

**ClickHouse 作为时序数据库替代**
ClickHouse 不是严格的 TSDB，但在金融时序场景表现优异：
- 列存储 + 向量化执行 -> 聚合查询极快
- `PARTITION BY toYYYYMMDD()` -> 天然时间分区
- `TTL` -> 自动过期旧数据
- 支持完整的 SQL -> 学习成本低
- 压缩率高 -> TB 级数据存储友好

**时序数据库的独有功能**（ClickHouse 部分支持）
- 自动降采样（Downsampling）：将秒级数据自动聚合为分钟/小时级
- 数据保留策略（Retention Policy）：自动删除过期数据
- 连续查询（Continuous Query）：预计算常用聚合

## Application Example

L2 数据的时序特征分析：
```
写入模式：每天收盘后批量导入当天数据（追加写入，不更新）
查询模式1：查某天全市场数据做截面因子分析（按时间范围）
查询模式2：查某只股票近一年走势（按 code + 时间范围）
数据生命周期：近期数据频繁查询（热），历史数据偶尔查询（冷）
```

这些特征决定了 L2 数据适合用时序优化的数据库存储。

## Common Misconceptions

1. "时序数据库只能存时间序列" -> 不是，只是对时序场景有特殊优化
2. "ClickHouse 是时序数据库" -> 严格来说不是，它是通用 OLAP 数据库，但具备时序数据库的核心能力
3. "时序数据库都很快" -> 快是相对的，取决于具体场景和配置

## Connections
- [[Database Partitioning]] -- 时序数据库通常自动按时间分区
- [[MongoDB vs MySQL vs ClickHouse]] -- ClickHouse 作为时序数据库替代
- [[L2 Market Data Storage Strategy]] -- L2 数据的时序特征与存储选型

## References
