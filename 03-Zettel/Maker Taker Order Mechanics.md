---
id: 202605011401
title: Maker Taker Order Mechanics
created: 2026-05-01T14:01
updated: "2026-05-11T20:00"
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
Taker 是市价单方，分为 taker_buy（市价买入）和 taker_sell（市价卖出）；Maker 是限价单方，分为 maker_buy（限价买挂单）和 maker_sell（限价卖挂单）。每笔成交恰好配对一个 Maker 和一个 Taker。`volume = taker_buy_volume + taker_sell_volume`，流动性由 Maker 提供（order book 上的挂单），Taker 消耗流动性（吃单让 order book 变薄）。关键是看谁主动：自己的限价买单被成交时，自己是 Maker 而非 Taker，主动吃你单的人才是 Taker，所以这笔 volume 计入 taker_sell_volume 而非 taker_buy_volume。

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
