---
id: 202605011400
title: Volume vs Quote Volume
created: 2026-05-01T14:00
updated: "2026-05-12T22:00"
tags:
  - type/zettel
  - domain/quant
  - mastery/2-familiar
aliases: []
---
# Volume vs Quote Volume

## Core Definition
Volume 是以基础货币（base currency）计量的成交量，Quote Volume 是以报价货币（quote currency）计量的成交金额。两者描述同一批交易，但单位不同。

## My Understanding
Volume 是以 BTC 为单位计量的成交量，Quote Volume 是以 USDT/USDC 计量的成交量。需要 quote volume 是为了更好地比较不同币种的实际成交金额，因为不同币种的价值差距巨大，volume 无法直接比较。

## Why It Matters
因子分析的核心是截面比较——每天把所有币种放在一起排名。不同币种的 base currency 量纲不同（1 BTC vs 1000 SHIB），无法直接用 volume 比较。Quote volume 统一到报价货币量纲，是做截面因子分析的前提。

## Technical Details
以 `BTCUSDT` 为例：
- `volume`：以 BTC 计量的成交量（如 500 BTC）
- `quote_volume`：以 USDT 计量的成交金额（如 43,000,000 USDT）
- 关系：`quote_volume ≈ volume × average_price`

Binance K线数据中两者都已预计算，无需手动转换。

## Application Example
计算"流动性因子"时，用 `quote_volume` 而非 `volume` 来衡量币种的日成交金额，确保 BTC 和山寨币在同一个量纲下可比。

## Common Misconceptions
- 误用 volume 做截面比较，忽略了不同币种的单位差异
- quote 在交易对中翻译为"报价"，是定价单位的意思

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子数据基础
- [[Maker Taker Order Mechanics]] -- volume 的组成与 maker/taker 的关系
