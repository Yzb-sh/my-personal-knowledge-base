---
id: 202605011402
title: Cross-Sectional vs Time-Series Data
created: 2026-05-01T14:02
updated: 2026-05-01T14:02
tags:
  - type/zettel
  - domain/quant
  - mastery/2-familiar
aliases: []
---
# Cross-Sectional vs Time-Series Data

## Core Definition
Time-series（时序）维度关注单个资产随时间的变化；Cross-sectional（截面）维度关注同一时间点所有资产的横向比较。因子分析需要同时支持两种维度。

## My Understanding
操作A（计算 BTC 的 20 日动量）是时序维度——需要某个资产过去 20 天的数据。操作B（比较今天所有币种的动量排名）是截面维度——需要今天所有资产的数据。按"每天一个文件"的结构，截面操作方便，时序操作麻烦。理想方案是把所有数据放进一张大表（日期×币种），通过过滤支持两种操作。

## Why It Matters
因子研究的两个核心步骤依赖不同维度：
1. 因子计算（如 20 日动量）→ 时序操作
2. 截面排名和 IC 计算 → 截面操作

数据组织方式直接影响研究效率。Panel 结构（date × symbol）是最通用的选择。

## Technical Details
- 时序操作：过滤 `symbol == "BTCUSDT"`，获取该资产的时间序列
- 截面操作：过滤 `date == "2025-03-28"`，获取该日所有资产的横截面
- Panel 数据：二维表，行为 (date, symbol) 组合，列为特征值
- 对于 Binance 1 分钟数据，先聚合为日频再构建 panel，可将 ~50 万文件压缩到一张表

## Application Example
计算动量因子并做 IC 分析：
1. 时序：对每个币种计算过去 20 天收益率（因子值）
2. 截面：每天按因子值排名，与未来收益做相关性分析（IC）

## Common Misconceptions
- 按单资产文件存储看似直观，但每次截面分析都要遍历所有文件
- 按单日文件存储有利于截面分析，但时序分析需要跨文件读取

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子研究数据基础
- [[Volume vs Quote Volume]] -- 截面比较需要统一量纲
