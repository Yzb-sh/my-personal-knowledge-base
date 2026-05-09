---
id: "202605091830"
title: "Quantile Portfolio Testing"
created: "2026-05-09T18:30"
updated: "2026-05-09T18:30"
tags:
  - type/zettel
  - domain/quant
  - domain/python
  - mastery/1-introduced
aliases: []
---
# Quantile Portfolio Testing

## Core Definition
分位数组合测试是将资产按因子值在截面上排序并等量分成 N 组，计算每组的平均收益率，通过检验各组收益是否单调递减以及多空组合（最高组 - 最低组）的盈利能力来评估因子的实际可交易性。

## My Understanding
IC 告诉你因子值与未来收益是否相关，但它没有反映收益率在实际分组中的分布——有可能相关性完全集中在少数资产上，大部分区间毫无关系。分位数组合测试解决了这个问题：把所有币种按因子值从小到大分成等量的组，看每组的平均收益是否单调递减。分位数就是不同排名区间，每个区间的样本数相同；组合是指将不同分位组合起来，比如多空组合就是做多因子值最高的一组、做空最低的一组。如果组 1 到组 5 的收益单调递减，说明因子的预测能力在整个截面上是均匀分布的，不只是一个极端组在撑场面。

## Why It Matters
IC 是因子的"平均预测能力"指标，但实际交易需要回答一个更具体的问题：如果我买入因子值最高的 N 个资产、卖空最低的，能不能赚钱？分位数组合测试就是这个问题的直接回答。它还能发现 IC 无法捕捉的非单调关系（如 U 型分布），以及因子在不同值区间的预测能力是否均匀。

## Technical Details

**截面分位数分组 — `pd.qcut`**
```python
df['group'] = df.groupby('date')[factor_col].transform(
    lambda x: pd.qcut(x, q, labels=range(1, q + 1))
)
```
- `pd.qcut(series, N)` — 按分位数切成 N 个等量区间（每组样本数相同）
- `pd.cut(series, N)` — 按值的固定宽度切成 N 个区间（每组范围相同，样本数不一定等）
- `pd.qcut` 是顶层函数，不是 Series 方法：正确 `pd.qcut(x, 5)`，错误 `x.qcut(5)`
- `labels=range(1, q+1)` 产生整数标签 1,2,...,q，不是字符串

**分位组合收益 — `unstack()`**
```python
port_ret = df.groupby(['date', 'group'])[return_col].mean().unstack()
```
- `groupby([date, group]).mean()` 返回 MultiIndex Series（两层索引：date, group）
- `.unstack()` 将索引的第二层（group）展开为列，得到宽格式 DataFrame
- 宽格式：行=date，列=1,2,...,q，值=各组当天的平均前向收益率
- `stack()` 是 `unstack()` 的逆操作：列折叠回索引层，宽格式变长格式

**多空价差**
```python
port_ret['long_short'] = port_ret[1] - port_ret[q]
```
- 组 1 = 因子值最高（rank 最小）= 做多端
- 组 q = 因子值最低 = 做空端
- 正 IC 因子：做多组 1，做空组 q；负 IC 因子反过来

**累计净值 — `cumprod()`**
```python
net_value = (1 + port_ret['long_short']).cumprod()
```
- `cumprod()` = 累积乘积，逐项相乘，替代 for 循环计算净值
- 等价于循环 `nav[i] = nav[i-1] * (1 + ret[i])`，但向量化一行搞定
- 最后一个值 `net_value.iloc[-1]` 就是期末单位净值（初始为 1）

**年化 Sharpe Ratio**
```python
sharpe = port_ret['long_short'].mean() / port_ret['long_short'].std() * (365 ** 0.5)
```
- 年化收益 = 日均收益 × N
- 年化标准差 = 日标准差 × √N（因为方差可加性：N 天方差 = N × 单日方差，std = √(N × 日方差)）
- Sharpe = 年化收益 / 年化 std = (mean × N) / (std × √N) = mean / std × √N
- 加密货币 365 天交易，所以 N = 365

**分组单调性检验**
```python
port_ret[[1, 2, 3, 4, 5]].mean()
```
- 各组在整个样本期间的平均日收益
- 理想情况：组 1 > 组 2 > ... > 组 q，单调递减
- 非单调说明因子预测能力不均匀

**DataFrame 索引规则**
- `df[label]` — 按列名取列，返回 Series（不是取行！）
- `df.iloc[pos]` — 按位置取行（0-indexed），如 `.iloc[-1]` 取最后一行
- `df.loc[label]` — 按索引标签取行

**完整函数**
```python
def calc_quantile_portfolio(df: pd.DataFrame, factor_col: str, return_col: str, q: int) -> dict:
    df['group'] = df.groupby('date')[factor_col].transform(
        lambda x: pd.qcut(x, q, labels=range(1, q + 1))
    )
    port_ret = df.groupby(['date', 'group'])[return_col].mean().unstack()
    mean_ret = port_ret[list(range(1, q + 1))].mean()
    port_ret['long_short'] = port_ret[1] - port_ret[q]
    net_value = (1 + port_ret['long_short']).cumprod()
    ann_ret = (net_value.iloc[-1] - 1) / len(port_ret) * 365
    sharpe = port_ret['long_short'].mean() / port_ret['long_short'].std() * (365 ** 0.5)
    return {'net_value': net_value, 'mean_ret': mean_ret, 'ann_ret': ann_ret, 'sharpe': sharpe}
```

## Application Example
加密货币因子研究场景：458 个币种面板数据，计算 20 日动量因子的 Rank 标准化值，用 `pd.qcut` 分成 5 组。组 1（动量最强）到组 5（动量最弱）的平均日收益单调递减。多空组合（组 1 - 组 5）的年化 Sharpe > 2，说明因子在截面上具有均匀且显著的预测能力。

## Common Misconceptions
- 试图用 if-elif 手动分组分位数：`pd.qcut` 一行搞定，不需要手动判断每个分位区间
- 把 `pd.qcut` 当成 Series 方法调用（`x.qcut()`）：它是 Pandas 顶层函数，写法是 `pd.qcut(x, N)`
- 用字符串 `result['1']` 而非整数 `result[1]` 访问列：`labels=range(1,q+1)` 产生整数标签，列名是整数
- 混淆 DataFrame `df[label]` 与行操作：`df[label]` 是按列名取列，取行用 `.iloc[pos]` 或 `.loc[label]`
- 用 for 循环计算累计净值：`cumprod()` 是向量化方法，一行替代循环
- `net_value[-1]` 取最后一个值：索引是日期时行为不确定，应使用 `.iloc[-1]`
- 不知道 `unstack()` / `stack()`：`unstack` 把 MultiIndex 层展开为列（长→宽），`stack` 是逆操作
- 类型注解语法 `pd.DataFrame(): df`：正确写法是 `df: pd.DataFrame`（不加括号）
- 试图用 `df.endswith("_rank")` 自动匹配列名：DataFrame 没有这个方法，应该通过函数参数传入列名
- 忘记 `sqrt` 需要导入：用 `365 ** 0.5` 替代 `math.sqrt(365)` 无需 import

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子模型板块，因子评估体系
- [[MOC-Python]] -- Pandas 分位数组合操作的代码实现
- [[IC Analysis and Significance Testing]] -- 分位数组合测试是 IC 分析之后的下一步，验证因子的实际可交易性
- [[IC Decay and Half-Life Estimation]] -- 同属因子评估体系，IC Decay 测时间维度的衰减，分位数组合测截面维度的分组效果
- [[Cross-Sectional Factor Standardization]] -- 标准化后的因子值才能做截面分组和排序
- [[Factor Construction with Rolling Windows]] -- 分位数组合测试的输入是构建好的因子
- [[Pandas GroupBy Transform and Apply]] -- 分组操作的基础
- [[Pandas Series and DataFrame]] -- DataFrame 索引规则（df[] vs iloc vs loc）是分位组合代码的基础
- [[Cross-Sectional vs Time-Series Data]] -- 分位数组合是截面维度的操作
- [[Turnover Analysis and Transaction Costs]] -- 换手率分析验证分位组合扣费后的真实盈利能力

## References
- 因子分析教学 Module 3C（2026-05-09 会话）
