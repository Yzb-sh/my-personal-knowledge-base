---
id: "moc-20260427"
title: "MOC-Home"
created: "2026-04-27"
updated: "2026-04-27"
tags:
  - type/structure
---
# MOC-Home

个人成长型量化知识库主索引。所有知识地图的入口。

## Knowledge Domains

### [[MOC-Mathematics]] -- 数学基础
概率论、统计学、线性代数、微积分、优化、随机过程

### [[MOC-Python]] -- Python 编程
Python 基础、NumPy、Pandas、可视化、量化库

### [[MOC-SQL]] -- SQL 数据查询
基础查询、聚合连接、窗口函数、查询优化

### [[MOC-Quantitative-Strategy]] -- 量化策略
因子模型、策略开发、回测、风险管理、组合构建、执行

### [[MOC-Learning-Methods]] -- 学习方法论
Zettelkasten 笔记法、间隔复习、知识管理方法

## Quick Links
- [[00-Inbox/_Inbox-Home|收件箱]] -- 待处理的临时笔记
- [[04-Project/_Project-Home|项目]] -- 活跃研究项目

## Vault Stats
<!-- 用 Dataview 查询自动生成 -->
```dataview
TABLE length(rows) as 笔记数
FROM "03-Zettel"
FLATTEN tags as t
GROUP BY t
SORT 笔记数 DESC
```
