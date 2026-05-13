"""
Bar Quality Analysis for Cross-Sectional IC Feasibility
========================================================
Analyzes whether 5-minute bars have sufficient trading activity
for cross-sectional IC analysis on top 200 crypto symbols.

Questions answered:
1. Fraction of bars with zero/near-zero volume at different frequencies
2. How this varies across liquidity tiers (Top 10, Top 50-100, Top 150-200)
3. Comparison of 5min vs 15min vs 1h "meaningful" bar fractions
4. Autocorrelation of adjacent 5min cross-sectional returns (IC redundancy)
"""

import sys
import os
import time
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

sys.path.insert(0, 'D:/YZB/Projects/crypto-quant-fund/src')
from data_ingestion.database import KlineDB

DATA_ROOT = 'D:/YZB/Projects/crypto-quant-fund/data/processed/binance_1m_klines'

# ── Configuration ──────────────────────────────────────────────────────────
SAMPLE_START = '2024-06-01'
SAMPLE_END   = '2024-06-07'       # 7 days
N_SYMBOLS    = 100                 # top 100 by daily avg quote_volume
FREQUENCIES  = {
    '5min':  '5min',
    '15min': '15min',
    '1h':    '1h',
}

db = KlineDB()

# ── Step 1: Rank symbols by average daily quote_volume ─────────────────────
print("=" * 80)
print("STEP 1: Ranking symbols by liquidity (avg daily quote_volume)")
print("=" * 80)

# Load 1 day of data for ALL symbols to rank by liquidity
print(f"  Loading 1-day snapshot for {SAMPLE_START} ...")
all_syms = db.list_symbols()
print(f"  Total symbols in DB: {len(all_syms)}")

# Load all symbols for one day - do it via direct parquet reads for speed
day_path = os.path.join(DATA_ROOT, '2024', '2024-06', '2024-06-01')
liquidity_records = []
files_in_day = [f for f in os.listdir(day_path) if f.endswith('.parquet')]

for i, f in enumerate(files_in_day):
    sym = f.replace('.parquet', '')
    df_day = pd.read_parquet(os.path.join(day_path, f))
    avg_qv = df_day['quote_volume'].mean()
    liquidity_records.append({'symbol': sym, 'avg_quote_volume_1min': avg_qv})

liq_df = pd.DataFrame(liquidity_records).sort_values('avg_quote_volume_1min', ascending=False).reset_index(drop=True)
liq_df['rank'] = range(1, len(liq_df) + 1)

print(f"\n  Liquidity ranking summary (top 10):")
for _, row in liq_df.head(10).iterrows():
    print(f"    #{int(row['rank']):3d}  {row['symbol']:20s}  avg_1min_qv = ${row['avg_quote_volume_1min']:>15,.0f}")

print(f"\n  Liquidity ranking summary (rank 45-55):")
for _, row in liq_df.iloc[44:55].iterrows():
    print(f"    #{int(row['rank']):3d}  {row['symbol']:20s}  avg_1min_qv = ${row['avg_quote_volume_1min']:>15,.0f}")

print(f"\n  Liquidity ranking summary (rank 95-105):")
for _, row in liq_df.iloc[94:105].iterrows():
    print(f"    #{int(row['rank']):3d}  {row['symbol']:20s}  avg_1min_qv = ${row['avg_quote_volume_1min']:>15,.0f}")

# Select top N symbols
top_symbols = liq_df.head(N_SYMBOLS)['symbol'].tolist()

# ── Step 2: Load 1-min data for top N symbols, resample manually ──────────
print("\n" + "=" * 80)
print(f"STEP 2: Loading 1-min data for top {N_SYMBOLS} symbols")
print(f"  Period: {SAMPLE_START} to {SAMPLE_END}")
print("=" * 80)

t0 = time.time()
df_all = db.get_klines_batch(top_symbols, SAMPLE_START, SAMPLE_END,
                              columns=['symbol','datetime','open','high','low','close',
                                       'volume','quote_volume','count'])
t1 = time.time()
print(f"  Loaded {len(df_all):,} rows in {t1-t0:.1f}s")
print(f"  Unique symbols: {df_all['symbol'].nunique()}")
print(f"  Date range: {df_all['datetime'].min()} to {df_all['datetime'].max()}")

# ── Step 3: Resample to different frequencies ─────────────────────────────
print("\n" + "=" * 80)
print("STEP 3: Resampling to 5min / 15min / 1h")
print("=" * 80)

def resample_group(group, freq):
    """Resample a single symbol's 1-min data to target frequency."""
    g = group.set_index('datetime').sort_index()
    resampled = g.resample(freq).agg({
        'open':   'first',
        'high':   'max',
        'low':    'min',
        'close':  'last',
        'volume': 'sum',
        'quote_volume': 'sum',
        'count':  'sum',
    }).dropna(subset=['close'])
    resampled['symbol'] = group['symbol'].iloc[0]
    return resampled.reset_index()

results = {}
for freq_name, freq_val in FREQUENCIES.items():
    print(f"  Resampling to {freq_name} ...")
    t0 = time.time()
    grouped = df_all.groupby('symbol')
    frames = []
    for sym, grp in grouped:
        frames.append(resample_group(grp, freq_val))
    df_freq = pd.concat(frames, ignore_index=True)
    results[freq_name] = df_freq
    t1 = time.time()
    print(f"    {len(df_freq):,} rows in {t1-t0:.1f}s")

# Merge liquidity rank
df_all_merged = df_all.merge(liq_df[['symbol','rank']], on='symbol', how='left')

# ── Step 4: Bar quality metrics by frequency ──────────────────────────────
print("\n" + "=" * 80)
print("STEP 4: Bar quality metrics at each frequency")
print("=" * 80)

def compute_bar_quality(df_freq, freq_name):
    """Compute quality metrics for a given frequency's bars."""
    # Price range as fraction of close
    df_freq = df_freq.copy()
    df_freq['price_range_pct'] = np.where(
        df_freq['close'] > 0,
        (df_freq['high'] - df_freq['low']) / df_freq['close'] * 100,
        0
    )

    metrics = {
        'total_bars': len(df_freq),
        'zero_volume': (df_freq['volume'] == 0).sum(),
        'zero_volume_pct': (df_freq['volume'] == 0).mean() * 100,
        'lt_1000_usdt': (df_freq['quote_volume'] < 1000).sum(),
        'lt_1000_usdt_pct': (df_freq['quote_volume'] < 1000).mean() * 100,
        'lt_5000_usdt': (df_freq['quote_volume'] < 5000).sum(),
        'lt_5000_usdt_pct': (df_freq['quote_volume'] < 5000).mean() * 100,
        'lt_10000_usdt': (df_freq['quote_volume'] < 10000).sum(),
        'lt_10000_usdt_pct': (df_freq['quote_volume'] < 10000).mean() * 100,
        'price_range_lt_001pct': (df_freq['price_range_pct'] < 0.01).sum(),
        'price_range_lt_001pct_pct': (df_freq['price_range_pct'] < 0.01).mean() * 100,
        'price_range_lt_01pct': (df_freq['price_range_pct'] < 0.1).sum(),
        'price_range_lt_01pct_pct': (df_freq['price_range_pct'] < 0.1).mean() * 100,
        'price_range_lt_1pct_pct': (df_freq['price_range_pct'] < 1.0).mean() * 100,
        'mean_quote_volume': df_freq['quote_volume'].mean(),
        'median_quote_volume': df_freq['quote_volume'].median(),
        'p25_quote_volume': df_freq['quote_volume'].quantile(0.25),
        'p10_quote_volume': df_freq['quote_volume'].quantile(0.10),
        'mean_price_range_pct': df_freq['price_range_pct'].mean(),
        'median_price_range_pct': df_freq['price_range_pct'].median(),
        'mean_trades': df_freq['count'].mean(),
        'zero_trades_pct': (df_freq['count'] == 0).mean() * 100,
    }
    return metrics

all_metrics = {}
for freq_name in FREQUENCIES:
    m = compute_bar_quality(results[freq_name], freq_name)
    all_metrics[freq_name] = m
    print(f"\n  {freq_name} bar quality (all {N_SYMBOLS} symbols, 7 days):")
    print(f"    Total bars:             {m['total_bars']:>10,}")
    print(f"    Zero volume:            {m['zero_volume_pct']:>10.2f}%  ({m['zero_volume']:,} bars)")
    print(f"    quote_volume < $1K:     {m['lt_1000_usdt_pct']:>10.2f}%  ({m['lt_1000_usdt']:,} bars)")
    print(f"    quote_volume < $5K:     {m['lt_5000_usdt_pct']:>10.2f}%  ({m['lt_5000_usdt']:,} bars)")
    print(f"    quote_volume < $10K:    {m['lt_10000_usdt_pct']:>10.2f}%  ({m['lt_10000_usdt']:,} bars)")
    print(f"    price_range < 0.01%:    {m['price_range_lt_001pct_pct']:>10.2f}%")
    print(f"    price_range < 0.1%:     {m['price_range_lt_01pct_pct']:>10.2f}%")
    print(f"    price_range < 1.0%:     {m['price_range_lt_1pct_pct']:>10.2f}%")
    print(f"    Zero trades (count=0):  {m['zero_trades_pct']:>10.2f}%")
    print(f"    Mean quote_volume:      ${m['mean_quote_volume']:>14,.0f}")
    print(f"    Median quote_volume:    ${m['median_quote_volume']:>14,.0f}")
    print(f"    P10 quote_volume:       ${m['p10_quote_volume']:>14,.0f}")
    print(f"    P25 quote_volume:       ${m['p25_quote_volume']:>14,.0f}")
    print(f"    Mean price range:       {m['mean_price_range_pct']:>10.4f}%")
    print(f"    Median price range:     {m['median_price_range_pct']:>10.4f}%")
    print(f"    Mean trades/bar:        {m['mean_trades']:>10.1f}")

# ── Step 5: Breakdown by liquidity tier ───────────────────────────────────
print("\n" + "=" * 80)
print("STEP 5: Bar quality by LIQUIDITY TIER")
print("=" * 80)

TIERS = {
    'Top 10':     (1, 10),
    'Top 11-30':  (11, 30),
    'Top 31-50':  (31, 50),
    'Top 51-75':  (51, 75),
    'Top 76-100': (76, 100),
    # Extended tiers if we have the data
}

tier_results = {}

for freq_name in FREQUENCIES:
    print(f"\n  --- {freq_name} bars ---")
    df_freq = results[freq_name].copy()
    # Merge rank
    df_freq = df_freq.merge(liq_df[['symbol','rank']], on='symbol', how='left')

    for tier_name, (lo, hi) in TIERS.items():
        df_tier = df_freq[(df_freq['rank'] >= lo) & (df_freq['rank'] <= hi)]
        if len(df_tier) == 0:
            continue

        df_tier['price_range_pct'] = np.where(
            df_tier['close'] > 0,
            (df_tier['high'] - df_tier['low']) / df_tier['close'] * 100,
            0
        )

        zero_vol = (df_tier['volume'] == 0).mean() * 100
        lt_1k = (df_tier['quote_volume'] < 1000).mean() * 100
        lt_5k = (df_tier['quote_volume'] < 5000).mean() * 100
        lt_10k = (df_tier['quote_volume'] < 10000).mean() * 100
        pr_lt_01 = (df_tier['price_range_pct'] < 0.01).mean() * 100
        pr_lt_1  = (df_tier['price_range_pct'] < 0.1).mean() * 100
        mean_qv = df_tier['quote_volume'].mean()
        med_qv = df_tier['quote_volume'].median()
        mean_pr = df_tier['price_range_pct'].mean()
        med_pr = df_tier['price_range_pct'].median()
        mean_trades = df_tier['count'].mean()

        key = (freq_name, tier_name)
        tier_results[key] = {
            'zero_vol_pct': zero_vol,
            'lt_1k_pct': lt_1k,
            'lt_5k_pct': lt_5k,
            'lt_10k_pct': lt_10k,
            'pr_lt_001_pct': pr_lt_01,
            'pr_lt_01_pct': pr_lt_1,
            'mean_qv': mean_qv,
            'med_qv': med_qv,
            'mean_pr': mean_pr,
            'med_pr': med_pr,
            'mean_trades': mean_trades,
            'n_bars': len(df_tier),
            'n_syms': df_tier['symbol'].nunique(),
        }

        print(f"    {tier_name:14s}  ({df_tier['symbol'].nunique():2d} syms, {len(df_tier):5,} bars):")
        print(f"      zero_vol={zero_vol:5.2f}%  <$1K={lt_1k:5.2f}%  <$5K={lt_5k:5.2f}%  <$10K={lt_10k:5.2f}%")
        print(f"      pr<0.01%={pr_lt_01:5.2f}%  pr<0.1%={pr_lt_1:5.2f}%")
        print(f"      mean_qv=${mean_qv:>14,.0f}  med_qv=${med_qv:>14,.0f}")
        print(f"      mean_pr={mean_pr:.4f}%  med_pr={med_pr:.4f}%")
        print(f"      mean_trades/bar={mean_trades:.0f}")

# ── Step 6: "Meaningful bar" composite score ──────────────────────────────
print("\n" + "=" * 80)
print("STEP 6: Meaningful bar definition and composite score")
print("=" * 80)

print("""
  Definition of "meaningful" bar:
    - quote_volume >= $1,000  (sufficient dollar turnover)
    - price_range >= 0.01%    (some price discovery)
    - trades >= 10            (enough market participants)
""")

for freq_name in FREQUENCIES:
    df_freq = results[freq_name].copy()
    df_freq = df_freq.merge(liq_df[['symbol','rank']], on='symbol', how='left')
    df_freq['price_range_pct'] = np.where(
        df_freq['close'] > 0,
        (df_freq['high'] - df_freq['low']) / df_freq['close'] * 100,
        0
    )

    meaningful = (
        (df_freq['quote_volume'] >= 1000) &
        (df_freq['price_range_pct'] >= 0.01) &
        (df_freq['count'] >= 10)
    )
    pct_meaningful = meaningful.mean() * 100

    print(f"  {freq_name}: {pct_meaningful:.2f}% of bars are 'meaningful' ({meaningful.sum():,} / {len(df_freq):,})")

    # By tier
    for tier_name, (lo, hi) in TIERS.items():
        mask_tier = (df_freq['rank'] >= lo) & (df_freq['rank'] <= hi)
        tier_data = df_freq[mask_tier]
        if len(tier_data) == 0:
            continue
        tier_meaningful = (
            (tier_data['quote_volume'] >= 1000) &
            (tier_data['price_range_pct'] >= 0.01) &
            (tier_data['count'] >= 10)
        )
        pct = tier_meaningful.mean() * 100
        print(f"    {tier_name:14s}: {pct:6.2f}% meaningful  ({tier_meaningful.sum():>5,} / {len(tier_data):>5,})")

# ── Step 7: 5min IC redundancy - autocorrelation of cross-sectional returns ─
print("\n" + "=" * 80)
print("STEP 7: 5min IC redundancy analysis")
print("=" * 80)

print("  Computing cross-sectional returns and rank correlation (IC) between adjacent bars...")

# Use 5min data
df_5m = results['5min'].copy()
df_5m = df_5m.merge(liq_df[['symbol','rank']], on='symbol', how='left')

# Compute per-bar returns (close-to-close)
df_5m = df_5m.sort_values(['symbol','datetime']).reset_index(drop=True)
df_5m['ret'] = df_5m.groupby('symbol')['close'].pct_change()
df_5m = df_5m.dropna(subset=['ret'])

# Get unique timestamps
timestamps = sorted(df_5m['datetime'].unique())
print(f"  Total 5min bars: {len(timestamps)}")
print(f"  Symbols per bar (approx): {df_5m.groupby('datetime')['symbol'].count().median():.0f}")

# Compute Spearman rank correlation (IC) between returns at bar t and bar t+1
from scipy.stats import spearmanr

ics = []
for i in range(len(timestamps) - 1):
    t0_data = df_5m[df_5m['datetime'] == timestamps[i]][['symbol','ret']].set_index('symbol')
    t1_data = df_5m[df_5m['datetime'] == timestamps[i+1]][['symbol','ret']].set_index('symbol')

    # Inner join on symbols present in both bars
    common = t0_data.index.intersection(t1_data.index)
    if len(common) < 20:
        continue

    rho, pval = spearmanr(t0_data.loc[common, 'ret'], t1_data.loc[common, 'ret'])
    ics.append({
        'timestamp': timestamps[i],
        'next_timestamp': timestamps[i+1],
        'ic': rho,
        'pval': pval,
        'n_common': len(common),
    })

ic_df = pd.DataFrame(ics)

if len(ic_df) > 0:
    print(f"\n  Adjacent 5min bar IC statistics ({len(ic_df)} bar pairs):")
    print(f"    Mean IC:           {ic_df['ic'].mean():.6f}")
    print(f"    Median IC:         {ic_df['ic'].median():.6f}")
    print(f"    Std IC:            {ic_df['ic'].std():.6f}")
    print(f"    |IC| > 0.05:       {(ic_df['ic'].abs() > 0.05).mean()*100:.1f}%")
    print(f"    |IC| > 0.02:       {(ic_df['ic'].abs() > 0.02).mean()*100:.1f}%")
    print(f"    IC significantly != 0 at 5%: {(ic_df['pval'] < 0.05).mean()*100:.1f}%")
    print(f"    Mean common syms:  {ic_df['n_common'].mean():.0f}")
    print(f"    IC 5th percentile: {ic_df['ic'].quantile(0.05):.6f}")
    print(f"    IC 95th percentile:{ic_df['ic'].quantile(0.95):.6f}")

    # Also compute IC at 15min and 1h for comparison
    print("\n  --- Cross-sectional return autocorrelation at different lags ---")
    for lag_name, lag_bars in [('1 bar (5min)', 1), ('3 bars (15min)', 3), ('6 bars (30min)', 6), ('12 bars (1h)', 12)]:
        lag_ics = []
        for i in range(len(timestamps) - lag_bars):
            t0_data = df_5m[df_5m['datetime'] == timestamps[i]][['symbol','ret']].set_index('symbol')
            t1_data = df_5m[df_5m['datetime'] == timestamps[i+lag_bars]][['symbol','ret']].set_index('symbol')
            common = t0_data.index.intersection(t1_data.index)
            if len(common) < 20:
                continue
            rho, _ = spearmanr(t0_data.loc[common, 'ret'], t1_data.loc[common, 'ret'])
            lag_ics.append(rho)
        lag_ics = np.array(lag_ics)
        print(f"    {lag_name:20s}: mean_IC={np.mean(lag_ics):.6f}, std={np.std(lag_ics):.6f}, "
              f"|IC|>0.05={np.mean(np.abs(lag_ics)>0.05)*100:.1f}%")

    # Compute actual cross-sectional factor IC (like a simple momentum factor)
    # At each bar, rank symbols by their return over the last N bars,
    # then see how that predicts the next-bar return
    print("\n  --- Momentum factor IC at 5min frequency ---")
    for lookback in [1, 3, 6, 12]:
        factor_ics = []
        for i in range(lookback, len(timestamps) - 1):
            # Factor: cumulative return over lookback
            past_data = {}
            for j in range(lookback):
                bar_data = df_5m[df_5m['datetime'] == timestamps[i-j]][['symbol','ret']].set_index('symbol')
                if j == 0:
                    for sym in bar_data.index:
                        past_data[sym] = bar_data.loc[sym, 'ret']
                else:
                    for sym in past_data:
                        if sym in bar_data.index:
                            past_data[sym] = (1 + past_data[sym]) * (1 + bar_data.loc[sym, 'ret']) - 1

            factor_df = pd.DataFrame({'factor': past_data})

            # Forward return
            fwd_data = df_5m[df_5m['datetime'] == timestamps[i+1]][['symbol','ret']].set_index('symbol')
            fwd_df = fwd_data.loc[fwd_data.index.intersection(factor_df.index)]
            factor_df = factor_df.loc[fwd_df.index]

            if len(factor_df) < 20:
                continue
            rho, _ = spearmanr(factor_df['factor'], fwd_df['ret'])
            factor_ics.append(rho)

        factor_ics = np.array(factor_ics)
        print(f"    {lookback}-bar momentum ({lookback*5}min lookback): mean_IC={np.mean(factor_ics):.6f}, "
              f"std={np.std(factor_ics):.6f}, |IC|>0.05={np.mean(np.abs(factor_ics)>0.05)*100:.1f}%")

# ── Step 8: Summary comparison table ──────────────────────────────────────
print("\n" + "=" * 80)
print("STEP 8: Summary comparison table")
print("=" * 80)

# Build a clean summary DataFrame
summary_rows = []
for freq_name in FREQUENCIES:
    df_freq = results[freq_name].copy()
    df_freq = df_freq.merge(liq_df[['symbol','rank']], on='symbol', how='left')
    df_freq['price_range_pct'] = np.where(
        df_freq['close'] > 0,
        (df_freq['high'] - df_freq['low']) / df_freq['close'] * 100,
        0
    )

    for tier_name, (lo, hi) in TIERS.items():
        df_tier = df_freq[(df_freq['rank'] >= lo) & (df_freq['rank'] <= hi)]
        if len(df_tier) == 0:
            continue
        meaningful = (
            (df_tier['quote_volume'] >= 1000) &
            (df_tier['price_range_pct'] >= 0.01) &
            (df_tier['count'] >= 10)
        ).mean() * 100

        summary_rows.append({
            'Frequency': freq_name,
            'Tier': tier_name,
            'Bars': len(df_tier),
            'Zero_Vol%': (df_tier['volume'] == 0).mean() * 100,
            '<$1K%': (df_tier['quote_volume'] < 1000).mean() * 100,
            '<$5K%': (df_tier['quote_volume'] < 5000).mean() * 100,
            'Meaningful%': meaningful,
            'Med_QV($)': df_tier['quote_volume'].median(),
            'Med_PR(%)': df_tier['price_range_pct'].median(),
        })

summary_df = pd.DataFrame(summary_rows)
print("\n" + summary_df.to_string(index=False))

# ── Final verdict ─────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("VERDICT: Is 5min cross-sectional IC viable?")
print("=" * 80)

# Gather key stats for top 100 at 5min
df_5m_tier = results['5min'].copy()
df_5m_tier = df_5m_tier.merge(liq_df[['symbol','rank']], on='symbol', how='left')
df_5m_tier['price_range_pct'] = np.where(
    df_5m_tier['close'] > 0,
    (df_5m_tier['high'] - df_5m_tier['low']) / df_5m_tier['close'] * 100,
    0
)

top100 = df_5m_tier[df_5m_tier['rank'] <= 100]
meaningful_5m_top100 = ((top100['quote_volume'] >= 1000) &
                         (top100['price_range_pct'] >= 0.01) &
                         (top100['count'] >= 10)).mean() * 100

top50 = df_5m_tier[df_5m_tier['rank'] <= 50]
meaningful_5m_top50 = ((top50['quote_volume'] >= 1000) &
                        (top50['price_range_pct'] >= 0.01) &
                        (top50['count'] >= 10)).mean() * 100

bot50 = df_5m_tier[(df_5m_tier['rank'] > 50) & (df_5m_tier['rank'] <= 100)]
meaningful_5m_bot50 = ((bot50['quote_volume'] >= 1000) &
                        (bot50['price_range_pct'] >= 0.01) &
                        (bot50['count'] >= 10)).mean() * 100

ic_mean = ic_df['ic'].mean()
print(f"""
  Key findings for 5min bars (top 100 symbols, 7-day sample):
    - Top 50 meaningful bar %:   {meaningful_5m_top50:.1f}%
    - Top 51-100 meaningful %:   {meaningful_5m_bot50:.1f}%
    - Top 100 meaningful bar %:  {meaningful_5m_top100:.1f}%

  Adjacent 5min bar IC:
    - Mean: {ic_mean:.4f}
    - This measures cross-sectional rank autocorrelation between adjacent bars
    - Low IC means adjacent bars carry independent information (good for sampling)
    - High IC means adjacent bars are redundant (should use longer bars)

  RECOMMENDATION:
    - If meaningful% < 80% for a tier at 5min, that tier needs 15min or 1h
    - If adjacent 5min IC is low (|IC| < 0.05), 5min adds information
    - If adjacent 5min IC is high (|IC| > 0.1), 5min is redundant, use 15min
""")
