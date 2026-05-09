---
id: 202605011401
title: Maker Taker Order Mechanics
created: 2026-05-01T14:01
updated: 2026-05-01T14:01
tags:
  - type/zettel
  - domain/quant
  - mastery/1-introduced
aliases: []
---
# Maker Taker Order Mechanics

## Core Definition
每笔交易都有一个 Maker（挂单方）和一个 Taker（吃单方）。Maker 提供流动性（挂限价单等待成交），Taker 消耗流动性（主动吃单成交）。

## My Understanding
Volume 由主动买入量和主动卖出量组成：`volume = taker_buy_volume + taker_sell_volume`。挂一个限价买单等待成交，自己是 Maker；当别人用市价卖单吃掉这个挂单时，对方是 Taker。所以这笔交易的 volume 不会计入 taker_buy_volume，而是计入 taker_sell_volume。如果下一个市价买单买了 10 个 BTC，这 10 BTC 同时计入 volume 和 taker_buy_volume，因为 taker_buy_volume 是 volume 的子集。

## Why It Matters
`taker_buy_volume / volume` 这个比率反映买方主动力量。比率 > 0.5 说明多头力量强，< 0.5 说明空头力量强。这本身可以作为一个因子（买卖力量不平衡因子）。

## Technical Details
- `taker_buy_volume`：主动买入成交量（taker 在买方）
- `taker_sell_volume = volume - taker_buy_volume`：主动卖出成交量（taker 在卖方）
- 每笔成交恰好有一个 Taker 和一个 Maker
- 限价单（limit order）挂单时是 Maker，被成交时对方是 Taker
- 市价单（market order）立即成交，下单者永远是 Taker

## Application Example
构建"订单流不平衡因子"：`(taker_buy_volume - taker_sell_volume) / volume`，衡量某币种在一段时间内的买卖力量对比。

## Common Misconceptions
- 误以为自己的限价买单被成交时会算入 taker_buy_volume——实际上你是 Maker，主动吃你单的人才是 Taker
- 误以为 taker_buy_volume 和 volume 是两个独立的数据——前者是后者的子集

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子数据基础
- [[Volume vs Quote Volume]] -- volume 的不同计量维度
