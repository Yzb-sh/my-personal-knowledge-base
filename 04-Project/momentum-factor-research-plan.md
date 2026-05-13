---
id: proj-20260511
title: 动量因子研究计划书
created: 2026-05-11
updated: 2026-05-11
tags: [type/project, domain/quant, status/active]
---

# 动量因子完整研究计划书

> **项目周期**: 2023-01 ~ 2025-12（数据覆盖）
> **目标**: 从原始数据出发，完成一次完整的动量因子研究，产出可实盘部署的策略框架
> **工作目录**: `D:\YZB\Projects\crypto-quant-fund\notebooks\factor_research\mom_00`

---

## 1. 研究概述

### 1.1 研究目标

1. **因子发现**：在 6 大类动量因子（62 变体）中，筛选出在加密货币日内交易中持续有效的因子
2. **策略构建**：将选出的因子合成为组合信号，确定最优持仓周期和调仓频率
3. **样本外验证**：在未参与因子选择的数据上验证策略的鲁棒性
4. **实盘对接**：研究流程与参数设计与实盘运行一致，可直接迁移

### 1.2 研究框架

| 阶段 | 目的 | 数据范围 | 产出 |
|------|------|---------|------|
| 阶段 1：因子发现 | 哪种动量定义有效？ | 2023-01 ~ 2025-06 | Top 3-5 因子 |
| 阶段 2：因子深入 | 最优参数、衰减、组合 | 2023-01 ~ 2025-06 | 合成因子、持仓周期 |
| 阶段 3：Walk-Forward OOS | 实盘可行性验证 | 2025-07 ~ 2025-12 | OOS 收益曲线、绩效指标 |

---

## 2. 研究参数配置

所有参数定义为全局常量，便于统一管理和敏感性分析：

```python
# ============================================================
# 核心参数
# ============================================================
FREQUENCY = '15min'           # K线频率: '5min' | '15min'
IC_FREQUENCY = '1h'           # IC评估频率: 'same' | '1h'
START_DATE = '2023-01-01'
END_DATE = '2025-12-31'

# 宇宙参数
N_SYMBOLS = 200               # 目标宇宙大小
UNIVERSE_UPDATE_FREQ = 7      # 宇宙更新频率（天）
LIQUIDITY_LOOKBACK = 30       # 流动性排名回看（天）
MIN_VOL_PERCENTILE = 25       # 最低波动率分位数

# 滚动窗口参数
WINDOWS_TRAIN = 7000          # 训练窗口（bars）—— 主分析尺度
WINDOWS_TEST = UNIVERSE_UPDATE_FREQ  # 测试窗口
WINDOWS_MULTIPLIERS = [0.4, 1.0, 2.1]  # 多尺度: 短(3000)/中(7000)/长(15000)

# 因子参数
FORMATION_PERIODS = [6, 12, 24, 48, 96]   # 形成期（bars）
SKIP_PERIODS = [0, 1, 2, 3]               # 跳过近期 bars
HOLDING_PERIODS = [1, 3, 6, 12, 24]       # 前向收益期限（bars）

# 交易参数
FEE_RATE = 5e-4               # Binance taker 费率
N_QUANTILES = 5               # 分位数组合数
REBALANCE_BARS = 4            # 调仓间隔（FREQUENCY bars）：15min×4=1h

# 统计参数
IC_METHOD = 'spearman'        # Rank IC
NW_LAG = None                 # Newey-West 滞后阶数（None = auto T^(1/3)）
MIN_PIR = 0.55                # 最低正IC比率
MIN_MEAN_IC = 0.02            # 最低平均IC
MIN_IC_SHARPE = 0.15          # 最低IC Sharpe

# 衍生常量
BARS_PER_DAY = {'5min': 288, '15min': 96, '1h': 24}
BARS_PER_YEAR = {k: v * 365 for k, v in BARS_PER_DAY.items()}
```

### 2.1 频率参数说明

**FREQUENCY**（K线频率）：决定因子计算的数据粒度。5min = 高分辨率但噪声大；15min = 平衡选择。

**IC_FREQUENCY**（IC 评估频率）：决定截面 IC 的采样间隔。设为 `1h` 时，因子仍从 FREQUENCY bars 计算，但每 1h 采样一次做截面相关性。理由：
- 相邻 5min bar 的 IC 高度自相关（实测 ρ(1) ≈ -0.06，bar 级冗余）
- 聚合到 1h 后，IC 观测更接近独立，有效样本量不会被自相关大幅稀释
- 数据实测证实：Top 200 币种在 5min bar 上零成交量比例为 0%，但 5.9% 的 bar 价格变动 < 0.1%

**建议**：第一轮用 FREQUENCY=15min + IC_FREQUENCY=1h 跑通全流程，确认结果合理后再测试 FREQUENCY=5min。

---

## 3. 数据管线

### 3.1 数据源

- **原始数据**：Binance 1min K线，Parquet 格式，~50 万个文件
- **路径**：`D:\YZB\Projects\crypto-quant-fund\data\processed\binance_1m_klines\`
- **访问方式**：KlineDB（DuckDB 后端，只读），支持 `resample` 参数
- **机器**：255 GB 内存，128 核，无内存瓶颈

### 3.2 面板构建流程

```
Step 1: 获取全部候选 symbol（~640个）
Step 2: 粗筛：剔除数据覆盖 < 30 天的僵尸币 → ~500 个候选
Step 3: KlineDB.get_klines_batch() + resample 批量加载
        按 FREQUENCY 聚合，拼接为 panel DataFrame
Step 4: 保存为 panel_{FREQUENCY}.parquet（全量候选，约 100M 行/15min）
```

**关键设计**：面板 = 全量候选数据，宇宙 = 动态掩码。分析时才按当前宇宙过滤。

### 3.3 数据列

| 列名 | 类型 | 说明 |
|------|------|------|
| symbol | str | 交易对（如 BTCUSDT） |
| datetime | datetime64 | 时间戳 |
| open/high/low/close | float64 | OHLC |
| volume | float64 | 成交量 |
| quote_volume | float64 | 成交额（USDT） |
| count | int64 | 成交笔数 |
| taker_buy_volume | float64 | 主动买入量 |
| taker_buy_quote_volume | float64 | 主动买入额 |

---

## 4. 宇宙筛选

### 4.1 动态宇宙机制

**核心设计**：每 UNIVERSE_UPDATE_FREQ 天重新筛选，模拟实盘行为。

```
每个 UNIVERSE_UPDATE_FREQ 天:
  1. 用过去 LIQUIDITY_LOOKBACK 天的日线数据
  2. 计算每个 symbol 的:
     - 平均日 quote_volume（流动性）
     - 实现波动率（日收益率的 std）
  3. 过滤: 波动率 > MIN_VOL_PERCENTILE 分位数
  4. 排名: 按 quote_volume 降序
  5. 取 Top N_SYMBOLS
```

### 4.2 进入条件

- 数据历史 ≥ 24h（过滤上市不到一天的币种）
- 波动率 > 最低分位数（过滤稳定币和僵尸币）
- 流动性排名在 Top N_SYMBOLS 内

### 4.3 退出条件

- 不再满足上述任一条件 → 自动移出宇宙
- 回测中：已持有的币种被移出 → 下一期持仓归零（模拟清仓）

### 4.4 面板中的处理

```python
# 对每个时间点，标记哪些 symbol 在宇宙中
panel['in_universe'] = panel.apply(universe_mask, axis=1)
# 分析时只使用 in_universe 的数据
df = panel[panel['in_universe']]
```

---

## 5. 动量因子定义（6 大类 62 变体）

### 5.1 公共基础

```python
# 对数收益率（所有因子共享）
panel['log_ret'] = panel.groupby('symbol')['close'].transform(
    lambda x: np.log(x / x.shift(1))
)
```

### 5.2 MOM_CS：截面动量（~20 变体）

**学术来源**：Jegadeesh & Titman (1993)

**公式**：`MOM_CS(J, S) = sum(log_ret[t-S-J : t-S], J bars)`

**含义**：过去 J 根 bar 的累计对数收益率，跳过最近 S 根 bar。

**Skip 期的作用**：最近 1-3 根 bar 的收益率可能包含微结构噪声（bid-ask bounce），跳过后信号更干净。

```python
panel[f'mom_cs_{J}_{S}'] = panel.groupby('symbol')['log_ret'].transform(
    lambda x: x.shift(S).rolling(J, min_periods=J).sum()
)
```

**参数网格**：J ∈ [6, 12, 24, 48, 96] × S ∈ [0, 1, 2, 3] = 20 变体

**15min 下对应时间**：J=6→1.5h, J=12→3h, J=24→6h, J=48→12h, J=96→24h

### 5.3 MOM_RA：风险调整动量（~20 变体）

**学术来源**：Blitz & Vliet (2008)

**公式**：`MOM_RA(J, S) = MOM_CS(J, S) / std(log_ret, J bars)`

**含义**：动量的信噪比。加密货币波动率离散极大（BTC 日波动 2% vs 小币 15%），除以波动率消除"只是因为波动大所以涨得多"的假象。

```python
mom_raw = panel.groupby('symbol')['log_ret'].transform(
    lambda x: x.shift(S).rolling(J, min_periods=J).sum()
)
mom_std = panel.groupby('symbol')['log_ret'].transform(
    lambda x: x.shift(S).rolling(J, min_periods=J).std()
)
panel[f'mom_ra_{J}_{S}'] = mom_raw / mom_std
```

**参数网格**：同 MOM_CS，20 变体

### 5.4 MOM_VW：成交量加权动量（~4 变体）

**含义**：高成交量 bar 的价格变动更有信息含量（价格发现发生在成交量大的时刻）。按成交量份额加权的收益率。

**公式**：`MOM_VW(J) = sum(ret_i × vol_share_i, i in [t-J, t])`

```python
panel['vol_share'] = panel.groupby('symbol').apply(
    lambda g: g['volume'] / g['volume'].rolling(J, min_periods=J).sum()
).reset_index(level=0, drop=True)
panel['ret_x_volshare'] = panel['log_ret'] * panel['vol_share']
panel[f'mom_vw_{J}'] = panel.groupby('symbol')['ret_x_volshare'].transform(
    lambda x: x.shift(1).rolling(J, min_periods=J).sum()
)
```

**参数网格**：J ∈ [12, 24, 48, 96] = 4 变体（跳过 J=6，太短不够做成交量加权）

### 5.5 MOM_CON：动量一致性（~4 变体）

**学术来源**：Grinblatt & Moskowitz (2004)

**公式**：`MOM_CON(J) = count(log_ret > 0, J bars) / J`

**含义**：过去 J 根 bar 中，有多少比例是涨的？两个累计收益相同的币种，持续小涨（80% 阳线）比偶尔暴涨（20% 阳线）的信号更可靠。

```python
panel['pos_ret'] = (panel['log_ret'] > 0).astype(int)
panel[f'mom_con_{J}'] = panel.groupby('symbol')['pos_ret'].transform(
    lambda x: x.shift(1).rolling(J, min_periods=J).mean()
)
```

**参数网格**：J ∈ [12, 24, 48, 96] = 4 变体

### 5.6 MOM_ED：指数衰减动量（~5 变体）

**含义**：等权求和（MOM_CS）vs 指数加权（MOM_ED）。近因效应在日内加密市场可能更强——1 小时前的动量比 6 小时前的更有预测力。

**公式**：`MOM_ED(J) = EMA(log_ret, span=J)`

```python
panel[f'mom_ed_{J}'] = panel.groupby('symbol')['log_ret'].transform(
    lambda x: x.shift(1).ewm(span=J, min_periods=J).mean()
)
```

**参数网格**：J ∈ [6, 12, 24, 48, 96] = 5 变体

### 5.7 MOM_UD：涨跌分解（~9 变体）

**含义**：加密货币上涨和下跌的动力学不对称。"拉盘"驱动的动量（少数大阳线）和"抛售"驱动的动量（多数小阴线）可能预测力不同。

**公式**：
```
MOM_UP(J) = sum(max(log_ret, 0), J bars)
MOM_DN(J) = sum(min(log_ret, 0), J bars)
MOM_UD(J) = MOM_UP(J) + |MOM_DN(J)|   ← 合并信号
```

```python
panel['up_ret'] = panel['log_ret'].clip(lower=0)
panel['dn_ret'] = panel['log_ret'].clip(upper=0)
panel[f'mom_up_{J}'] = panel.groupby('symbol')['up_ret'].transform(
    lambda x: x.shift(1).rolling(J, min_periods=J).sum()
)
panel[f'mom_dn_{J}'] = panel.groupby('symbol')['dn_ret'].transform(
    lambda x: x.shift(1).rolling(J, min_periods=J).sum()
)
panel[f'mom_ud_{J}'] = panel[f'mom_up_{J}'] + panel[f'mom_dn_{J}'].abs()
```

**参数网格**：J ∈ [12, 24, 48]，每个 J 有 3 个子因子（up/dn/ud）= 9 变体

### 5.8 因子标准化

所有因子在 IC 分析前必须做截面标准化：

```python
# Step 1: 截面 Winsorize（1st/99th 分位数截断）
panel[f'{factor}_win'] = panel.groupby('datetime')[factor].transform(
    lambda x: x.clip(x.quantile(0.01), x.quantile(0.99))
)
# Step 2: Rank 标准化（稳健性最优）
panel[f'{factor}_rank'] = panel.groupby('datetime')[f'{factor}_win'].transform(
    lambda x: x.rank(ascending=True, pct=True)
)
```

**ascending=True**：高 rank = 高动量 = 预期正收益，与正 IC 约定一致。

### 5.9 变体汇总

| 因子族 | 变体数 | 关键参数 |
|--------|--------|---------|
| MOM_CS 截面动量 | 20 | J × S |
| MOM_RA 风险调整 | 20 | J × S |
| MOM_VW 成交量加权 | 4 | J |
| MOM_CON 一致性 | 4 | J |
| MOM_ED 指数衰减 | 5 | J |
| MOM_UD 涨跌分解 | 9 | J × 子因子 |
| **合计** | **62** | |

---

## 6. 分析框架

### 6.1 阶段 1：因子发现（滚动窗口 IC）

**核心思路**：在研究期（2023-01 ~ 2025-06）上滚动窗口计算 IC，用三个指标筛选因子。

**指标定义**：
- **PIR（正 IC 比率）**：跨窗口中 IC > 0 的比例。直接衡量因子方向一致性。
- **Mean IC**：跨窗口的平均 IC。衡量效应大小。
- **IC Sharpe**：mean IC / std IC（跨窗口）。衡量稳定性。

**筛选标准**：PIR > 0.55 且 |Mean IC| > 0.02 且 IC Sharpe > 0.15

**多重检验校正**：62 变体 × 5 持有期 = 310 个 IC 测试，传统 t > 2.0 阈值会产生大量假阳性。采用 FDR (Benjamini-Hochberg) 校正控制假发现率，或参考 Harvey-Liu-Zhu (2016) 将显著性阈值提高到 t > 3.0。多尺度验证本身是多重检验的缓解手段，但最终入选因子必须在三个尺度上通过**校正后**的阈值。

**多尺度验证**：一个因子需在短/中/长三个窗口尺度上同时通过筛选才算入选。

| 尺度 | 窗口长度 | 15min 对应 | 用途 |
|------|---------|-----------|------|
| 短 | ~3,000 bars | ~31 天 | 短期 regime IC |
| 中 | ~7,000 bars | ~73 天 | 主分析尺度 |
| 长 | ~15,000 bars | ~156 天 | 稳定性检验 |

**窗口滑动步长**：步长 = 窗口长度 × `WINDOW_STEP_RATIO`（默认 1/3），多尺度自动适配。

```python
WINDOW_STEP_RATIO = 1/3    # 步长/窗口长度比例，1/2 纳入敏感性分析
# 中尺度步长: int(7000 * 1/3) = 2333 bars (~24天)
# 短尺度步长: int(3000 * 1/3) = 1000 bars (~10天)
# 长尺度步长: int(15000 * 1/3) = 5000 bars (~52天)
```

**为什么用比例制步长**：固定步长（如每天 96 bars）在长窗口下重叠率过高（98.6%），导致相邻窗口 IC 估计几乎相同。比例制步长确保不同尺度的窗口都有合理独立性（重叠 ~66.7%）。

### 6.2 IC 计算细节

**前向收益计算**：

```python
for H in HOLDING_PERIODS:
    panel[f'fwd_ret_{H}'] = panel.groupby('symbol')['close'].transform(
        lambda x: np.log(x.shift(-H) / x)
    )
```

**截面 IC 计算**（在 IC_FREQUENCY 采样点上）：

```python
# 聚合到 IC_FREQUENCY 后计算
ic_series = df_slice.groupby(df_slice['datetime'].dt.floor(IC_FREQUENCY)).apply(
    lambda x: x[factor_rank].corr(x[f'fwd_ret_{H}'], method='spearman')
)
```

**显著性检验**：Newey-West 校正（`calc_ic_stats()` 函数，来自知识库笔记）。

### 6.3 阶段 2：因子深入分析

对选出的 Top 3-5 因子：

**2a. IC 衰减与半衰期**：
- 计算因子在 H = 1, 2, 3, 6, 12, 24, 48 bars 前向收益上的 IC
- 指数拟合估算半衰期：`ln(IC) = ln(IC₀) - λ·h`，半衰期 = ln2/λ
- 半衰期决定最优持仓周期
- IC 在极端行情日（BTC 单日涨跌 > 10%）的表现
- 因子"失效"频率：连续 N 个窗口 IC < 0 的比例

**2b. 分位数组合测试**：
- `pd.qcut(5)` 分组，等权组合收益
- 多空价差 = 最高组 - 最低组
- 单调性检验：Spearman 秩相关检验分组收益是否单调递增/递减
- 累计净值曲线

**2c. 换手率分析**：
- 每个调仓日的成员变化率：`1 - |A∩B| / |A|`
- 交易成本：`换手率 × 2 × FEE_RATE`
- 净 Sharpe = 扣费后年化收益 / 年化波动

**2d. 因子相关性**：
- 候选因子间 Spearman 相关矩阵
- |corr| > 0.8 的冗余对，保留 IC Sharpe 更高的

**2e. 因子合成**：
- 等权 / IC 加权 / ICIR 加权
- 权重仅用训练期 IC 统计量计算（避免前视偏差）
- Walk-Forward 权重更新：expanding window 每月重算

**2f. 仓位管理**：
- 反波动率仓位：`weight = 1/vol` 在组内归一化
- 多空暴露：多头组总权重 = 空头组总权重 = 0.5

**2g. 基准对比**：
- 等权做多宇宙（buy-and-hold benchmark）：每期等权持有当前宇宙所有币种
- 随机因子 IC 分布：随机排名（permutation test）的 IC 统计量分布，用于校准 PIR/Mean IC 的显著性基线
- 简单动量 baseline：MOM_CS(J=24, S=1) 单因子，作为"最朴素动量"参照

**2h. 市场 Regime 分析**：
- BTC 20日实现波动率作为 regime 指标，按中位数划分高/低波动 regime
- 因子在两种 regime 下的 IC 分别统计（PIR、Mean IC、IC Sharpe）
- 分位数组合在两种 regime 下的多空价差对比
- 如果因子只在单侧 regime 有效，需在研究结论中明确标注此限制

### 6.3b 风险管理规则（实盘必需）

在因子合成和 OOS 验证中，仓位管理需遵守以下约束：

| 规则 | 参数 | 说明 |
|------|------|------|
| 单资产最大仓位 | ≤ 5% | 防止单币种过度集中 |
| 最大组合波动率 | 日波动 ≤ 2% | 控制整体风险敞口 |
| 回撤熔断 | 回撤 > 10% 时减仓 50% | 极端行情保护 |
| 多/空组暴露中性 | 多 = 空 = 0.5 | 市场中性策略默认 |

**为什么需要这些规则**：加密市场极端行情频繁（BTC 单日涨跌 10%+ 并非罕见），纯反波动率仓位在尾部事件中可能产生巨大损失。回测中这些规则的效果需要量化评估（有/无规则的绩效对比）。

### 6.4 阶段 3：Walk-Forward OOS 验证

**验证期**：2025-07-01 ~ 2025-12-31

**流程**：
```
对验证期的每个 UNIVERSE_UPDATE_FREQ 天:
  1. 更新宇宙
  2. 用过去 WINDOWS_TRAIN bars 计算 IC → 更新合成权重
  3. 计算合成因子值
  4. 截面分组 → 确定多空持仓
  5. 按反波动率分配仓位
  6. 与上一期持仓对比 → 计算换手率和交易成本
  7. 记录扣费后收益
```

**绩效指标**：

| 指标 | 公式 | 良好阈值 |
|------|------|---------|
| OOS Sharpe（net） | mean(net_ret)/std(net_ret) × √(bars/year) | > 1.5 |
| OOS Max Drawdown | min(nav/cummax(nav) - 1) | > -20% |
| OOS Calmar | 年化收益/|最大回撤| | > 1.0 |
| OOS Mean IC | 截面 Rank IC 均值 | > 0.02 |
| Train/Test Sharpe 比 | OOS Sharpe / Train Sharpe | > 0.5 |

**OOS Regime 分段分析**（必做）：

数据仅覆盖到 2025-12，OOS 期仅 6 个月，可能无法覆盖完整的市场 regime 循环。必须做以下分段分析以缓解此限制：

```python
# BTC 20日实现波动率作为 regime 指标
btc_vol = panel[panel['symbol'] == 'BTCUSDT']['log_ret'].rolling(20 * 96).std()
regime = (btc_vol > btc_vol.median()).map({True: 'high_vol', False: 'low_vol'})
```

- 分别报告高波动期和低波动期的 Sharpe、Max DD、Mean IC
- 如果因子只在单一 regime 有效，需在研究结论中明确标注
- 标注风险：如果 OOS 全期处于单一 regime，结果泛化能力存疑

---

## 7. 敏感性分析

完成主分析后，对以下参数做对照实验：

| 参数 | 测试范围 | 目的 |
|------|---------|------|
| FREQUENCY | 5min, 15min | 信号粒度影响 |
| N_SYMBOLS | 150, 200, 300 | 宇宙大小影响 |
| UNIVERSE_UPDATE_FREQ | 3, 7, 14, 30 天 | 宇宙更新频率影响 |
| WINDOWS_TRAIN | 3000, 7000, 15000 | 训练窗口长度影响 |
| REBALANCE_BARS | 1h, 2h, 4h | 调仓频率影响 |
| FEE_RATE | 3e-4, 5e-4, 1e-3 | 手续费敏感性 |
| WINDOW_STEP_RATIO | 1/3, 1/2 | 窗口步长比例（独立性 vs 窗口数量） |

**参数稳定性检验**：IC(J, S) 热力图。如果出现"尖峰"（只有某个特定 J,S 组合有效），说明可能过拟合到该参数。

---

## 8. Notebook 结构

```
mom_00/
  00_config.py                  # 全局参数配置
  utils.py                      # 通用工具函数（IC计算、截面标准化、绩效统计等）
  factor_lib.py                 # 因子计算函数（每个因子族一个函数，可独立测试）
  00_data_exploration.ipynb     # 数据探索与质量分析（阶段 0）
  01_universe.ipynb             # 宇宙筛选 + 面板构建 → universe.csv, panel.parquet
  02_factor_construction.ipynb  # 6 大类因子计算 + 标准化 → panel_with_factors.parquet
  03_ic_analysis.ipynb          # 滚动 IC 筛选 + IC 衰减 → ic_results.csv
  04_quantile_portfolio.ipynb   # 分位数组合 + 换手率 → portfolio_results.csv
  05_factor_combination.ipynb   # 相关性 + 合成 + 仓位 → composite_factor.parquet
  06_oos_validation.ipynb       # Walk-Forward OOS + 绩效报告 → final_report.csv
  07_sensitivity.ipynb          # 参数敏感性分析 → sensitivity_results.csv
  output/                       # 频率特定的输出目录
    15min/
    5min/
  RESEARCH_PLAN.md              # 本计划书
  CLAUDE.md                     # 项目配置
```

**切换频率**：修改 `00_config.py` 中的 `FREQUENCY`，重新运行 01-06 即可。输出自动写入 `output/{FREQUENCY}/`。

---

## 9. 内存与性能

### 9.1 估算（15min 频率）

- 原始面板：~500 symbols × 140K bars × 10 columns × 8 bytes ≈ 5.6 GB
- 加入 62 因子列：~500 × 140K × 62 × 8 ≈ 34.7 GB
- 总计：~40 GB
- **机器内存 255 GB**，完全无压力

### 9.2 估算（5min 频率）

- 原始面板：~500 symbols × 420K bars × 10 columns × 8 bytes ≈ 16.8 GB
- 加入 62 因子列：~500 × 420K × 62 × 8 ≈ 104 GB
- 总计：~120 GB
- **仍然无压力**，但建议分批计算因子并保存中间结果

### 9.3 运行时间估算

- 面板加载：~10-20 分钟（KlineDB 按月加载 + 拼接）
- 因子计算：~20-30 分钟（62 变体 × 500 symbols，数据量翻倍）
- 滚动 IC：~20-30 分钟（~100 窗口 × 62 变体 × 5 持有期）
- 总计：**~60-80 分钟单次运行**

---

## 10. 研究问题清单

研究完成后应能回答：

1. 最优形成期 J 是多少？不同因子族的最优 J 是否一致？
2. Skip 期在 5min/15min 下是否重要？跳过 1-3 bar 的 IC 增益有多大？
3. 哪个因子族 IC Sharpe 最高？各族之间是否互补？
4. IC 衰减半衰期暗示的最优持仓周期？
5. 风险调整动量（MOM_RA）是否优于原始动量（MOM_CS）？
6. 成交量加权（MOM_VW）是否带来增量信息？
7. 上涨动量和下跌动量哪个预测力更强？
8. 最优调仓频率下的扣费后 Sharpe？
9. 样本外 Sharpe 衰减是否 < 50%？
10. 5min vs 15min 哪个频率的因子更有效？

---

## 11. 效率优化路线图（阶段 2）

完成基础 Pipeline（阶段 1）后，系统性优化数据处理效率。原则："先量化，再优化"——用 profiler 识别瓶颈，按收益排序逐一优化。

### 11.1 优化技术清单

| 优先级 | 技术 | 预期收益 | 适用场景 |
|--------|------|---------|---------|
| P0 | float32 替代 float64 | 50% 内存减少 | 全局 |
| P0 | 向量化 rolling（避免 lambda） | 3-5× 速度提升 | 因子计算 |
| P1 | 批量因子计算（分批处理 62 变体） | 30% 内存减少 | 02_factor_construction |
| P1 | DuckDB 做 IC 计算 | 2-5× 速度提升 | 03_ic_analysis |
| P2 | NumPy cumsum trick 替代 rolling.sum | 5-10× 速度提升 | MOM_CS/MOM_RA |
| P2 | ProcessPoolExecutor 并行 IC 窗口 | 线性扩展（128核） | 03_ic_analysis |
| P3 | Polars 替代 Pandas | 3-5× 整体提升 | 全局重构（仅当需要 5min 高频数据时） |

### 11.2 优化流程

```
Step 1: 在阶段 1 每个 notebook 中用 %%timeit / time.perf_counter() 记录耗时
Step 2: 用 cProfile / line_profiler 分析 top 3 瓶颈
Step 3: 按 P0 → P1 → P2 顺序优化
Step 4: 每次优化后 benchmark 对比（优化前/后耗时 + 结果一致性校验）
Step 5: 产出性能对比报告
```

### 11.3 阶段 0 数据探索（前置）

在正式因子研究前，先花 2-3 天理解数据特征：
- 加载 1 个月数据子集，分析 NaN 模式、零成交量比例、价格跳跃频率
- 测试 KlineDB 批量加载速度、Pandas rolling 操作速度基线
- 学习 float32 vs float64 内存/速度差异
- 产出：数据质量摘要 + 效率基线

---

## 12. 关键参考

### 学术文献
- Jegadeesh & Titman (1993): 截面动量效应的奠基论文
- Moskowitz, Ooi & Pedersen (2012): 时序动量
- Blitz & Vliet (2008): 风险调整动量
- Grinblatt & Moskowitz (2004): 动量一致性
- Harvey, Liu & Zhu (2016): 多重检验与因子动物园问题

### 项目内资源
- KlineDB: `crypto-quant-fund/src/data_ingestion/database/kline_db.py`
- 因子库: `crypto-quant-fund/src/factors/momentum.py`
- 研究工具: `crypto-quant-fund/src/research/metrics.py`
- 知识库笔记: IC Analysis, IC Decay, Quantile Portfolio, Turnover, Factor Combination, Backtesting

---

## Connections

- [[IC Analysis and Significance Testing]] — IC 计算与 Newey-West 校正的核心函数
- [[IC Decay and Half-Life Estimation]] — IC 衰减曲线和半衰期估算方法
- [[Quantile Portfolio Testing]] — 分位数组合测试框架
- [[Turnover Analysis and Transaction Costs]] — 换手率和交易成本建模
- [[Factor Combination Methods]] — 因子合成方法
- [[Inverse Volatility Position Sizing]] — 反波动率仓位管理
- [[Backtesting with Transaction Costs]] — 回测框架
- [[Cross-Sectional Factor Standardization]] — 截面标准化方法
- [[Factor Construction with Rolling Windows]] — 因子构建代码模式
