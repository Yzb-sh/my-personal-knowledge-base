"""
ETF日线行情数据获取工具

Fallback链: AKShare/EastMoney → AKShare/Sina → yfinance
自动处理代理绕过、代码格式、日期格式、列名标准化
"""

import logging
import os
import re
import time

import pandas as pd

logger = logging.getLogger(__name__)


# ── 工具函数 ──────────────────────────────────────────────

def _parse_code(code: str) -> dict:
    """将各种格式的ETF代码标准化为各API所需的格式"""
    code = code.strip()
    num = re.sub(r'^(sh|sz|s\.?)', '', code, flags=re.IGNORECASE)

    if not num.isdigit():
        raise ValueError(f"无效的ETF代码: {code}")

    # 5/6/9开头 → 上交所, 0/1/2/3开头 → 深交所
    if num[0] in ('5', '6', '9'):
        exchange = 'sh'
    elif num[0] in ('0', '1', '2', '3'):
        exchange = 'sz'
    else:
        raise ValueError(f"无法识别交易所 (首位={num[0]}): {code}")

    return {
        'code': num,
        'exchange': exchange,
        'sina': f'{exchange}{num}',          # sh510300
        'em': num,                           # 510300
        'yf': f'{num}.SS' if exchange == 'sh' else f'{num}.SZ',
    }


def _parse_date(date_str: str) -> str:
    """统一为 YYYY-MM-DD"""
    s = date_str.strip()
    if re.match(r'^\d{8}$', s):
        return f'{s[:4]}-{s[4:6]}-{s[6:]}'
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s
    raise ValueError(f"无法解析日期: {date_str}")


# ── 数据源 A: AKShare / EastMoney ────────────────────────

def _fetch_em(info: dict, start: str, end: str, adjust: str) -> pd.DataFrame:
    """数据最全（支持复权、涨跌幅等），但对代理敏感"""
    import akshare as ak
    import requests

    # 绕过代理：清环境变量 + 禁用 requests 的系统代理检测
    _saved = {}
    for k in ('http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY'):
        v = os.environ.pop(k, None)
        if v is not None:
            _saved[k] = v

    _orig_init = requests.Session.__init__
    def _no_proxy_init(self, *a, **kw):
        _orig_init(self, *a, **kw)
        self.trust_env = False
    requests.Session.__init__ = _no_proxy_init

    try:
        adj_map = {'': '', 'qfq': 'qfq', 'hfq': 'hfq'}
        df = ak.fund_etf_hist_em(
            symbol=info['em'],
            period='daily',
            start_date=start.replace('-', ''),
            end_date=end.replace('-', ''),
            adjust=adj_map.get(adjust, ''),
        )
        if df is None or df.empty:
            raise ValueError("返回空数据")

        rename = {
            '日期': 'date', '开盘': 'open', '收盘': 'close',
            '最高': 'high', '最低': 'low', '成交量': 'volume',
            '成交额': 'amount', '振幅': 'amplitude', '涨跌幅': 'pct_chg',
            '涨跌额': 'chg', '换手率': 'turnover',
        }
        df = df.rename(columns=rename)

        std = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
        extra = [c for c in ('pct_chg', 'chg', 'amplitude', 'turnover') if c in df.columns]
        df = df[std + extra]

        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        for c in ('open', 'high', 'low', 'close'):
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').astype('Int64')
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        return df.reset_index(drop=True)
    finally:
        os.environ.update(_saved)
        requests.Session.__init__ = _orig_init


# ── 数据源 B: AKShare / Sina ────────────────────────────

def _fetch_sina(info: dict, start: str, end: str, adjust: str) -> pd.DataFrame:
    """最稳定：走新浪接口，不受代理影响，但无复权"""
    import akshare as ak

    if adjust:
        logger.warning("[Sina] 不支持复权，返回未复权数据")

    df = ak.fund_etf_hist_sina(symbol=info['sina'])
    if df is None or df.empty:
        raise ValueError("返回空数据")

    df['date'] = pd.to_datetime(df['date'])
    ts, te = pd.Timestamp(start), pd.Timestamp(end)
    df = df.loc[(df['date'] >= ts) & (df['date'] <= te)].copy()

    if df.empty:
        raise ValueError(f"{start}~{end} 范围内无数据")

    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df.reset_index(drop=True)


# ── 数据源 C: yfinance ───────────────────────────────────

def _fetch_yfinance(info: dict, start: str, end: str, adjust: str) -> pd.DataFrame:
    """国际源，代理友好，无成交额字段，内置限流重试"""
    import yfinance as yf

    ticker = yf.Ticker(info['yf'])
    last_err = None
    for attempt in range(4):
        try:
            df = ticker.history(
                start=start, end=end,
                auto_adjust=(adjust == 'qfq'),
            )
            if df is not None and not df.empty:
                break
            last_err = ValueError("返回空数据")
        except Exception as e:
            last_err = e
        if attempt < 3:
            wait = 5 * (2 ** attempt)  # 5s, 10s, 20s
            print(f"[yfinance] 第{attempt+1}次请求失败（{last_err}），{wait}s后重试…")
            time.sleep(wait)
    else:
        raise last_err

    df = df.reset_index()
    df['date'] = (
        pd.to_datetime(df['Date'])
        .dt.tz_localize(None)
        .dt.strftime('%Y-%m-%d')
    )
    df = df.rename(columns={
        'Open': 'open', 'High': 'high', 'Low': 'low',
        'Close': 'close', 'Volume': 'volume',
    })
    df['amount'] = pd.NA
    df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
    return df.reset_index(drop=True)


# ── 校验 ──────────────────────────────────────────────────

def _validate(df: pd.DataFrame) -> None:
    required = {'date', 'open', 'high', 'low', 'close', 'volume'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"缺少必要列: {missing}")
    if df.empty:
        raise ValueError("返回空DataFrame")
    for col in ('open', 'high', 'low', 'close'):
        if df[col].isna().all():
            raise ValueError(f"列 '{col}' 全部为NaN")


# ── 主函数 ────────────────────────────────────────────────

def get_etf_daily(
    code: str,
    start_date: str,
    end_date: str,
    adjust: str = '',
    max_retries: int = 1,
) -> pd.DataFrame:
    """
    获取ETF日线行情（多源 fallback + 自动重试）

    Fallback 顺序
    ─────────────
    A. AKShare/EastMoney  数据最全，支持复权，对代理敏感
    B. AKShare/Sina       最稳定，不受代理影响，无复权
    C. yfinance            国际源，代理友好，无成交额

    全部失败后重试一轮，仍然失败则抛出 RuntimeError。

    Parameters
    ----------
    code : str
        ETF代码: '510300', 'sh510300', 'SH510300' 均可
    start_date : str
        '2024-01-01' 或 '20240101'
    end_date : str
        '2024-12-31' 或 '20241231'
    adjust : str
        '' 不复权 | 'qfq' 前复权 | 'hfq' 后复权
        仅 EastMoney 源生效
    max_retries : int
        全部方法失败后额外重试轮次（默认1轮）

    Returns
    -------
    pd.DataFrame
        标准列: date, open, high, low, close, volume, amount, source
        EastMoney 额外列（如有）: pct_chg, chg, amplitude, turnover

    Raises
    ------
    RuntimeError
        所有数据源在重试后仍全部失败
    """
    info = _parse_code(code)
    start = _parse_date(start_date)
    end = _parse_date(end_date)

    # 需要复权时优先 yfinance（稳定且支持前复权），否则保留原顺序
    if adjust:
        methods = [
            ('yfinance', _fetch_yfinance),
            ('AKShare/EastMoney', _fetch_em),
            ('AKShare/Sina', _fetch_sina),
        ]
    else:
        methods = [
            ('AKShare/EastMoney', _fetch_em),
            ('AKShare/Sina', _fetch_sina),
            ('yfinance', _fetch_yfinance),
        ]

    all_errors: list[str] = []

    for attempt in range(1 + max_retries):
        for name, fn in methods:
            try:
                print(f"[{name}] 正在获取 {info['code']} 日线数据 ({start} ~ {end}) …")
                df = fn(info, start, end, adjust)
                _validate(df)
                df['source'] = name
                print(f"[{name}] 成功获取 {len(df)} 行数据")
                return df
            except Exception as e:
                msg = f"{name}(轮次{attempt + 1}): {e}"
                all_errors.append(msg)
                print(f"[{name}] 失败: {e}")

        if attempt < max_retries:
            wait = 2 ** (attempt + 1)
            logger.info(f"全部方法失败，{wait}s 后重试…")
            time.sleep(wait)

    detail = '\n'.join(f"  - {e}" for e in all_errors)
    raise RuntimeError(
        f"所有数据源均失败 ({info['code']}, {start}~{end}):\n{detail}"
    )


# ── CLI 快速测试 ──────────────────────────────────────────

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
    )

    df = get_etf_daily('510300', '2024-01-01', '2024-01-15')
    print(f"\n{'='*50}")
    print(f"数据源: {df['source'].iloc[0]}")
    print(f"行数: {len(df)}")
    print(df.to_string(index=False))
