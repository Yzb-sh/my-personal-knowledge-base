---
id: "202604271610"
title: "Processing Parquet with Python"
created: "2026-04-27T16:10"
updated: "2026-05-12T22:00"
tags:
  - type/zettel
  - domain/python
  - mastery/1-introduced
aliases: []
---
# Processing Parquet with Python

## Core Definition

使用 Python 处理 Parquet 格式文件的核心方法，涵盖读取、写入、查询、转换等操作。主要工具链：pandas（易用）、pyarrow（底层高性能）、polars（大数据场景推荐）。

## My Understanding

以前只会用 CSV（pd.read_csv），但 TB 级 L2 数据用 CSV 完全不现实。Parquet 的处理和 CSV 类似，pandas 的 API 几乎一样（read_parquet 对应 read_csv），关键区别是 Parquet 支持只读需要的列和按条件过滤——这是列存储的核心优势。

## Why It Matters

这是从"能用 Python 处理数据"到"能高效处理大规模数据"的关键技能。处理 L2 逐笔数据必须掌握 Parquet。

## Technical Details

**基础工具安装**
```bash
pip install pandas pyarrow fastparquet
# 可选：大数据场景用 polars
pip install polars
```

**1. 读取 Parquet**

```python
import pandas as pd

# 基本读取
df = pd.read_parquet("data.parquet")

# 只读需要的列（列存储的核心优势，大幅减少内存和 I/O）
df = pd.read_parquet("data.parquet",
    columns=["trade_time", "code", "price", "volume"])

# 按条件过滤读取（谓词下推，不加载无关数据到内存）
df = pd.read_parquet("data.parquet",
    filters=[("trade_date", "==", "2026-04-27")])

# 指定引擎
df = pd.read_parquet("data.parquet", engine="pyarrow")
```

**2. 写入 Parquet**

```python
# 基本写入
df.to_parquet("output.parquet", index=False)

# 指定压缩算法（默认 snappy）
df.to_parquet("output.parquet", index=False, compression="snappy")

# 按列分区存储（推荐：按日期分区）
df.to_parquet("L2_data/", partition_cols=["trade_date"], index=False)
# 生成目录结构：L2_data/trade_date=2026-04-27/part-0.parquet
```

**3. 查询与过滤**

```python
# 读取后过滤（先加载到内存，再过滤）
df = pd.read_parquet("data.parquet")
result = df[df["code"] == "000001"]

# 读取时过滤（推荐：谓词下推，更高效）
df = pd.read_parquet("data.parquet",
    filters=[("code", "==", "000001")])

# 复合条件
df = pd.read_parquet("data.parquet",
    filters=[
        ("trade_date", ">=", "2026-04-25"),
        ("trade_date", "<=", "2026-04-27"),
        ("code", "in", ["000001", "600000"])
    ])
```

**4. 增量追加数据**

```python
# 方法1：读取-合并-重写（适合小量追加）
df_existing = pd.read_parquet("data.parquet")
df_new = pd.read_csv("new_data.csv")  # 从 CSV 转 Parquet
df_combined = pd.concat([df_existing, df_new], ignore_index=True)
df_combined.to_parquet("data.parquet", index=False)

# 方法2：分区目录追加（推荐，适合按日期追加）
df_new.to_parquet("L2_data/", partition_cols=["trade_date"], index=False)
# 新日期自动创建新分区目录，不影响已有数据
```

**5. 处理大文件（内存不足时）**

```python
# 方法1：分块读取
import pyarrow.parquet as pq
parquet_file = pq.ParquetFile("huge_data.parquet")
for batch in parquet_file.iter_batches(batch_size=100000):
    df_batch = batch.to_pandas()
    # 处理每个批次
    process(df_batch)

# 方法2：使用 pyarrow.dataset 按分区读取
import pyarrow.dataset as ds
dataset = ds.dataset("L2_data/", format="parquet", partitioning="hive")
table = dataset.to_table(
    filter=ds.field("trade_date").isin(["2026-04-25", "2026-04-27"]),
    columns=["trade_time", "code", "price"]
)
df = table.to_pandas()
```

**6. CSV 转 Parquet**

```python
# 单个文件转换
df = pd.read_csv("L2_data_20260427.csv")
df.to_parquet("L2_data_20260427.parquet", index=False)

# 批量转换目录下所有 CSV
import os
csv_dir = "csv_files/"
for f in os.listdir(csv_dir):
    if f.endswith(".csv"):
        df = pd.read_csv(os.path.join(csv_dir, f))
        out_name = f.replace(".csv", ".parquet")
        df.to_parquet(os.path.join("parquet_files/", out_name), index=False)
```

**7. 查看元数据（不加载全部数据）**

```python
import pyarrow.parquet as pq

# 查看 Schema
pf = pq.ParquetFile("data.parquet")
print(pf.schema)

# 查看行数和列数
print(f"行数: {pf.metadata.num_rows}")
print(f"列数: {pf.metadata.num_columns}")
print(f"行组数: {pf.metadata.num_row_groups}")

# 查看各列统计信息（min/max/count）
for i in range(pf.metadata.num_columns):
    col = pf.metadata.row_group(0).column(i)
    print(f"{col.path_in_schema}: min={col.min}, max={col.max}")
```

## Application Example

**L2 逐笔数据日常处理流程**

```python
import pandas as pd
import pyarrow.dataset as ds

# 1. 读取特定日期的 L2 数据
df = pd.read_parquet(
    "L2_data/",
    columns=["trade_time", "code", "price", "volume", "bs_flag"],
    filters=[("trade_date", "==", "2026-04-27")]
)

# 2. 计算每只股票的日成交统计
daily_stats = df.groupby("code").agg(
    vwap=("price", lambda x: (x * df.loc[x.index, "volume"]).sum() / df.loc[x.index, "volume"].sum()),
    total_volume=("volume", "sum"),
    trade_count=("price", "count"),
    high=("price", "max"),
    low=("price", "min")
)

# 3. 保存分析结果
daily_stats.to_parquet("daily_stats.parquet", index=True)
```

## Common Misconceptions

1. "Parquet 和 CSV 的 pandas API 完全一样" -> 大部分一样，但 Parquet 支持 `filters` 和 `columns` 参数做文件级过滤，这是 CSV 没有的
2. "Parquet 文件不能查看内容" -> 可以用 `pd.read_parquet()` 快速查看，也可以用 DuckDB 直接查询
3. "大数据必须用 Spark" -> 不一定，Polars + Parquet 单机可以处理数十 GB 数据
4. "read_parquet 的 filters 能加速任何查询" -> 只有当过滤条件对应 Parquet 文件内的统计信息（min/max）或分区时才有效

## Connections
- [[Parquet File Format]] -- Parquet 格式的原理和优势
- [[L2 Market Data Storage Strategy]] -- L2 数据的完整存储方案
- [[Row Storage vs Column Storage]] -- 列存储原理支撑了 Parquet 的只读列优势

## References
