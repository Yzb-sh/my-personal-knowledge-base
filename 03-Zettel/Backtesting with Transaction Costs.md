---
id: "202605101002"
title: "Backtesting with Transaction Costs"
created: "2026-05-10T10:02"
updated: "2026-05-10T10:02"
tags:
  - type/zettel
  - domain/quant
  - domain/python
  - mastery/1-introduced
aliases: []
---
# Backtesting with Transaction Costs

## Core Definition
回测是用历史数据模拟真实交易，计算策略在扣除交易成本后的净表现。核心指标包括年化收益、Sharpe Ratio、最大回撤和 Calmar Ratio。交易成本基于仓位变化量（换手）计算，而非直接从收益率中扣除。

## My Understanding
回测就是算策略到底赚不赚钱。每天的收益 = 持仓收益 - 换仓手续费。持仓收益是每个币的 position * ret 的求和，手续费是仓位变化量的绝对值之和乘以费率。净收益用 cumprod 算出累计净值，用 cummax 算出历史高点，然后净值除以 cummax 减 1 就是回撤。Sharpe 用扣费后的净收益算，Calmar 是年化收益除以最大回撤的绝对值。

## Why It Matters
不扣费的回测是"纸上富贵"。加密货币虽然费率低（taker 5e-4），但高频再平衡的换手率累积起来会显著侵蚀收益。真实的策略评估必须包含交易成本。

## Technical Details

**回测时序**
1. t-1 日收盘后：观察因子值，计算 t 日的目标仓位 `position_t`
2. t 日开盘：从 `position_{t-1}` 调仓到 `position_t`，产生换手，付手续费
3. t 日持仓期间：仓位 `position_t` 赚取收益 `ret_t`
4. t 日净收益 = `sum(position_t * ret_t)` - `手续费_t`

**交易成本公式**
$$\text{cost}_t = \text{fee\_rate} \times \sum_i |\text{position}_{i,t} - \text{position}_{i,t-1}|$$

**累计净值 — `cumprod()`**
```python
net_value = (1 + result['net_ret']).cumprod()
```
- `cumprod()` = 累积乘积，逐项相乘
- 等价于 `nav[i] = nav[i-1] * (1 + ret[i])`，但向量化一行搞定

**最大回撤 — `cummax()`**
```python
cummax = net_value.cummax()
drawdown = net_value / cummax - 1
max_drawdown = drawdown.min()
```
- `cummax()` = 累计最大值，每个位置返回"到当前位置为止的历史最高值"
- `net_value / cummax - 1` = 当前净值相对历史高点的回撤幅度
- 比循环高效得多，是向量化的操作

**绩效指标**
```python
sharpe = result['net_ret'].mean() / result['net_ret'].std() * (365 ** 0.5)
ann_ret = (net_value.iloc[-1] - 1) / (len(net_value) - 1) * 365
calmar = ann_ret / abs(max_drawdown)
```
- Sharpe：年化风险调整收益，用**扣费后**净收益计算
- Calmar：年化收益 / 最大回撤绝对值，衡量每承受一单位最大损失获得多少收益

**完整回测函数**
```python
def backtest(df, fee_rate=0.0005):
    # 前一日仓位（按 symbol 分组 shift）
    df['fwd_position'] = df.groupby('symbol')['position'].shift(1)
    # 每日换手
    df_turnover = df.groupby('date')[['position', 'fwd_position']].apply(
        lambda x: (x['position'] - x['fwd_position']).abs().sum()
    ).rename('turnover')
    # 每日持仓收益
    df_ret = df.groupby('date')[['position', 'ret']].apply(
        lambda x: (x['position'] * x['ret']).sum()
    ).rename('ret')
    # 合并
    result = pd.concat([df_turnover, df_ret], axis=1)
    result['net_ret'] = result['ret'] - result['turnover'] * 2 * fee_rate
    # 绩效指标
    net_value = (1 + result['net_ret']).cumprod()
    sharpe = result['net_ret'].mean() / result['net_ret'].std() * (365 ** 0.5)
    ann_ret = (net_value.iloc[-1] - 1) / (len(net_value) - 1) * 365
    drawdown = net_value / net_value.cummax() - 1
    max_drawdown = drawdown.min()
    calmar = ann_ret / abs(max_drawdown)
    return {'ann_ret': ann_ret, 'max_drawdown': max_drawdown,
            'sharpe': sharpe, 'calmar': calmar, 'net_value': net_value}
```

**`pd.merge` vs `pd.concat`**
- `pd.merge`：按指定列匹配合并两个 DataFrame（需要 `on` 参数）
- `pd.concat`：按索引自动对齐拼接多个 Series 或 DataFrame
- 合并两个**共享索引的 Series**，用 `concat` 更简洁：`pd.concat([s1, s2], axis=1)`
- `axis=1`：水平拼接（左右并排），`axis=0`（默认）：垂直拼接（上下叠起来）

**Python 内置函数 vs Pandas 方法**
- `sum()`、`abs()`、`mean()` — Python 内置，适用于普通列表/数值
- `.sum()`、`.abs()`、`.mean()` — Pandas 方法，适用于 Series/DataFrame，自动处理 NaN
- 规则：操作 Pandas 对象用点号方法，操作普通 Python 数据用内置函数

## Application Example
加密货币多空策略回测：458 币种面板数据，ICIR 加权综合因子，反波动率仓位管理，每日再平衡。taker 费率 5e-4。计算每日换手产生的交易成本，扣除后计算净 Sharpe 和最大回撤，评估策略是否在扣费后仍有正收益。

## Common Misconceptions
- `cumprod()` 拼写为 `cumproud()`（本次会话犯 3 次）：正确拼写是 cumprod（cumulative product）
- `apply` 拼写为 `allpy`（本次会话犯 3 次）
- 运算优先级错误（本次会话犯 2 次）：`x['position'] * x['ret'].sum()` 先算 ret 的总和再乘 position，应该是 `(x['position'] * x['ret']).sum()` 先逐元素相乘再求和
- Sharpe 用扣费前 `ret` 而非 `net_ret`：应该评估策略的**真实**表现
- 手续费从收益率里直接扣（`position * (ret - fee)`）：手续费应基于仓位变化量（换手），不是每期固定扣除
- 用循环算最大回撤：`cummax()` 是向量化方法，一行替代循环
- `pd.concat` 和 `pd.merge` 混淆：concat 按索引对齐拼接，merge 按列匹配合并
- `groupby(...).apply(lambda x: ...)` 返回 Series 时没有列名：需要 `.rename('name')` 指定名称后才能在 concat 中正确显示

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于回测板块，绩效指标和交易成本建模
- [[MOC-Python]] -- cumprod、cummax、pd.concat、groupby apply 的代码实践
- [[Inverse Volatility Position Sizing]] -- 仓位计算是回测的直接前置步骤
- [[Factor Combination Methods]] -- 合成因子 → 仓位 → 回测的完整链路
- [[Turnover Analysis and Transaction Costs]] -- 换手率和交易成本模型在回测中的直接应用
- [[Quantile Portfolio Testing]] -- 分位数组合测试是简化的回测，这里扩展为带交易成本的完整版
- [[IC Analysis and Significance Testing]] -- Sharpe 与 ICIR 的关系（Sharpe ≈ ICIR × √N）

## References
- 因子分析教学 Module 4C（2026-05-09/10 会话）
