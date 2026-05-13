---
id: "202605101000"
title: "Factor Combination Methods"
created: "2026-05-10T10:00"
updated: "2026-05-10T10:00"
tags:
  - type/zettel
  - domain/quant
  - domain/python
  - mastery/1-introduced
aliases: []
---
# Factor Combination Methods

## Core Definition
因子合成是将多个单因子的标准化值按一定权重组合成一个综合信号（composite factor），用于生成统一的交易决策。三种主流加权方式：等权（equal）、IC 加权（IC weight）、ICIR 加权（ICIR weight）。

## My Understanding
等权就是把每个因子标准化后的 Z-score 直接加起来，每个因子占同样的权重。但每个因子的预测能力不同，所以应该给 IC 更高或 IR 更高的因子更大的权重。IC 加权用 mean IC 做权重，ICIR 加权用 IR（mean IC / std IC）做权重，后者同时考虑了预测能力和稳定性。直接用全样本 IC 做权重会有前视偏差（look-ahead bias），因为用了未来数据，所以实际上需要定期更新权重，比如每 20 个交易日重算一次。

## Why It Matters
单因子策略分散度不足，且多个因子可能互补（动量看趋势、波动率看风险、流动性看市场深度）。合成综合信号可以更全面地刻画资产特征，提升策略的稳健性和信息比率。

## Technical Details

**三种加权方案**

| 方案 | 权重公式 | 特点 |
|------|---------|------|
| 等权 | $w_i = 1/n$ | 最简单，无参数 |
| IC 加权 | $w_i = \overline{IC_i}$ | 只看预测能力 |
| ICIR 加权 | $w_i = IR_i = \overline{IC_i} / \sigma(IC_i)$ | 兼顾预测能力和稳定性 |

**合成函数 — `combine_factors`**
```python
def combine_factors(factor_dict, method='equal', value_col='factor_value', ic_stats=None):
    # Step 1: 取第一个因子作为初始 df，重命名值列为因子名
    key, df = list(factor_dict.items())[0]
    df.rename(columns={value_col: key}, inplace=True)
    # Step 2: 遍历剩余因子，重命名后按 (date, symbol) 合并
    for key, value in list(factor_dict.items())[1:]:
        value.rename(columns={value_col: key}, inplace=True)
        df = pd.merge(df, value, on=['date', 'symbol'])
    df_fac_columns = df.columns[2:]
    # Step 3: 按加权方式合成
    if method == 'equal':
        df[f'combine_value_{method}'] = df[df_fac_columns].sum(axis=1)
    elif method == 'ic':
        if ic_stats is None:
            raise ValueError('"ic" method needs "ic_stats"')
        for fac_name in df_fac_columns:
            weight = ic_stats.loc[fac_name, 'mean_ic']
            df[fac_name] = df[fac_name] * weight
        df[f'combine_value_{method}'] = df[df_fac_columns].sum(axis=1)
    elif method == 'icir':
        if ic_stats is None:
            raise ValueError('"icir" method needs "ic_stats"')
        for fac_name in df_fac_columns:
            weight = ic_stats.loc[fac_name, 'mean_ic'] / ic_stats.loc[fac_name, 'std_ic']
            df[fac_name] = df[fac_name] * weight
        df[f'combine_value_{method}'] = df[df_fac_columns].sum(axis=1)
    else:
        raise ValueError(f'Unknown method: {method}')
    return df
```

**ic_stats 数据结构**
- DataFrame，以因子名为索引，列包含 `mean_ic`、`std_ic`、`t_nw`、`p_nw`
- 通过 `ic_stats.loc['momentum', 'mean_ic']` 查询

**前视偏差与权重更新**
- 全样本 IC 统计量包含未来数据，直接用于加权会导致 look-ahead bias
- 实践中定期（如每 20 个交易日）用截至当天的历史数据重算 IC 统计量并更新权重

## Application Example
加密货币多因子策略：已测试 5 个因子（动量、反转、波动率、成交量、Amihud 流动性），各自有显著 IC。用 ICIR 加权合成综合信号，每月更新一次权重，避免前视偏差。

## Common Misconceptions
- `dict.values()[0]` 直接取下标会报错：`.values()` 返回 `dict_values` 视图对象，不能索引，需要 `list(dict.values())[0]`。`.items()` 同理，需要 `list(dict.items())[0]`
- rename 中 `'value_col'`（带引号）是字符串字面量，`value_col`（不带引号）才是变量：`rename(columns={value_col: key})` 而非 `rename(columns={'value_col': key})`
- `pd.merge` 不指定 `on` 参数时 Pandas 自动猜测列名，可能出错：应明确写 `on=['date', 'symbol']`
- 混淆 IC 和因子值：IC 是一个因子在某个日期的整体预测能力（一个标量），不是每个 (date, symbol) 上的值
- `f'{key}'` 和 `key` 效果相同，f-string 是多余的

## Connections
- [[MOC-Quantitative-Strategy]] -- 属于因子模型板块，因子组合与选择
- [[MOC-Python]] -- Pandas merge、dict 操作的代码实践
- [[IC Analysis and Significance Testing]] -- IC/IR 是因子合成的权重来源
- [[IC Decay and Half-Life Estimation]] -- IC 衰减影响权重更新的频率决策
- [[Quantile Portfolio Testing]] -- 合成因子的评估使用分位数组合测试
- [[Factor Construction with Rolling Windows]] -- 合成前的因子构建步骤
- [[Cross-Sectional Factor Standardization]] -- 合成前必须先对因子做截面标准化

## References
- 因子分析教学 Module 4A（2026-05-09/10 会话）
