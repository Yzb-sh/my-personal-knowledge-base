---
id: "202604271600"
title: "Parquet File Format"
created: "2026-04-27T16:00"
updated: "2026-05-12T22:00"
tags:
  - type/zettel
  - domain/python
  - mastery/1-introduced
aliases: []
---
# Parquet File Format

## Core Definition

Apache Parquet 是一种开源的列式存储文件格式，专为大数据分析场景设计。数据按列组织并压缩存储，支持高效的列裁剪和谓词下推（Predicate Pushdown），是处理 L2 等大规模数据的首选文件格式。

## My Understanding

Parquet 就是"列存储版的 CSV"。CSV 是纯文本行存储，每次读取必须加载所有列、解析文本。Parquet 是二进制列存储，只读需要的列、自带压缩和类型信息。对于 TB 级 L2 数据，Parquet 比 CSV 小 5-10 倍，查询快数十倍。以后处理 L2 数据应该用 Parquet 而不是 CSV。

## Why It Matters

CSV 是最常见的入门数据格式，但完全不适合大数据场景。从 CSV 切换到 Parquet 是数据处理能力提升的关键一步。

## Technical Details

**Parquet vs CSV 核心差异**

| 维度 | CSV | Parquet |
|------|-----|---------|
| 存储方式 | 行存储，纯文本 | 列存储，二进制 |
| 文件大小 | 大（无压缩） | 小 5-10 倍（内置 Snappy/Gzip 压缩 + 列式编码） |
| 读取速度 | 慢（解析文本 + 读全部列） | 快（二进制 + 只读需要的列） |
| 类型信息 | 无（全是字符串） | 有（保留完整 Schema） |
| 列裁剪 | 不支持（必须读全部列） | 支持（只读指定列） |
| 谓词下推 | 不支持 | 支持（在文件层面过滤行，不加载到内存） |
| 分区支持 | 无 | 原生支持（Hive-style 分区目录） |
| 人类可读 | 是 | 否（需要工具查看） |

**Parquet 文件内部结构**
```
Magic Number (PAR1)
├── Row Group 1 (行组，一批行)
│   ├── Column Chunk: trade_time (列块)
│   ├── Column Chunk: code
│   ├── Column Chunk: price
│   └── Column Chunk: volume
├── Row Group 2
│   └── ...
├── Footer (元数据：Schema、统计信息)
└── Footer Length + Magic Number
```

- **Row Group**：一组行的集合（通常几十 MB 到几百 MB）
- **Column Chunk**：一个 Row Group 中某列的数据
- **Footer**：存储 Schema、每列的 min/max 统计信息（用于谓词下推）

**压缩算法选择**
| 算法 | 压缩率 | 速度 | 推荐场景 |
|------|--------|------|----------|
| Snappy | 一般 | 极快 | 默认选择，读写频繁 |
| Gzip | 高 | 慢 | 存储归档，极少修改 |
| Zstd | 高 | 较快 | 平衡选择 |
| Brotli | 最高 | 最慢 | 极致压缩 |

**为什么 Parquet 压缩率高？**
1. 列式编码：同列数据类型相同，可用 delta encoding（整数列）、dictionary encoding（字符串列）等高效编码
2. 列内数据相似度高：如交易日期列大量重复值，压缩比极高
3. 内置压缩：编码后再用 Snappy/Gzip 等通用压缩

## Application Example

L2 逐笔数据的存储对比：
```
假设：每天 5000 万条记录，50 个字段

CSV 文件：
- 大小：约 15 GB/天
- 读取 price 列：必须读取全部 15 GB，解析文本

Parquet 文件（Snappy 压缩）：
- 大小：约 1.5-3 GB/天（压缩 5-10 倍）
- 读取 price 列：只读 price 列块，约 0.3 GB，无需解析文本
- 速度提升：约 50-100 倍
```

## Common Misconceptions

1. "Parquet 只能在 Spark/Hadoop 生态用" -> 不是，Python (pandas/pyarrow/polars) 原生支持
2. "Parquet 不能用 Excel 打开" -> 确实不能直接打开，但可以用 Python 快速查看
3. "Parquet 文件不能追加数据" -> 可以通过分区目录追加新分区，也可以读取-合并-重写
4. "Parquet 完全替代 CSV" -> CSV 在小数据、人工查看、跨系统交换场景仍有价值

## Connections
- [[Row Storage vs Column Storage]] -- Parquet 是列存储在文件层面的实现
- [[L2 Market Data Storage Strategy]] -- L2 数据用 Parquet 格式存储的具体方案
- [[Processing Parquet with Python]] -- 用 Python 读写和处理 Parquet 文件

## References
