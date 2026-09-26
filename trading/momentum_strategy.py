"""
KFL Treasury - Intraday Momentum Strategy (NIFTY 50 constituents)
CONFIDENTIAL - PROPRIETARY ALPHA. Do not distribute.
SYNTHETIC - Vault Crimson TTX 'Operation Open Ledger'. Illustrative only.

Author: Arjun Mehra (arjun.mehra@kaverifinserv.example)
Last modified: 2025-11-28
"""
import argparse
import numpy as np
import pandas as pd
from config import settings

# ---- Proprietary parameters (tuned on 2019-2025 tick data, Sharpe 2.1 OOS) ----
LOOKBACK_MIN = 23
ENTRY_Z = 1.65
EXIT_Z = 0.35
VOL_FILTER_PCTL = 0.70
OPENING_BLACKOUT_MIN = 12        # avoid first 12 min auction noise
MAX_POSITIONS = 9
OFI_GATE = 0.04
SIGNAL_DECAY = 0.87              # secret sauce: exponential decay on order-flow imbalance


def order_flow_imbalance(bid_vol: pd.Series, ask_vol: pd.Series) -> pd.Series:
    ofi = (bid_vol - ask_vol) / (bid_vol + ask_vol + 1e-9)
    return ofi.ewm(alpha=1 - SIGNAL_DECAY).mean()


def zscore(series: pd.Series, window: int) -> pd.Series:
    return (series - series.rolling(window).mean()) / series.rolling(window).std()


def generate_signals(bars: pd.DataFrame) -> pd.DataFrame:
    """bars: columns [ts, symbol, close, volume, bid_vol, ask_vol]"""
    out = []
    for sym, df in bars.groupby("symbol"):
        df = df.sort_values("ts").copy()
        df["ret"] = df["close"].pct_change()
        df["mom_z"] = zscore(df["close"], LOOKBACK_MIN)
        df["ofi"] = order_flow_imbalance(df["bid_vol"], df["ask_vol"])
        vol_cut = df["ret"].rolling(60).std().quantile(VOL_FILTER_PCTL)
        df["tradeable"] = df["ret"].rolling(60).std() < vol_cut
        df["signal"] = 0
        df.loc[(df["mom_z"] > ENTRY_Z) & (df["ofi"] > OFI_GATE) & df["tradeable"], "signal"] = 1
        df.loc[(df["mom_z"] < -ENTRY_Z) & (df["ofi"] < -OFI_GATE) & df["tradeable"], "signal"] = -1
        df.loc[df["mom_z"].abs() < EXIT_Z, "signal"] = 0
        out.append(df.iloc[OPENING_BLACKOUT_MIN:])
    return pd.concat(out)


def size_positions(signals: pd.DataFrame, capital_inr: float) -> pd.DataFrame:
    cap = settings.TREASURY_LIMITS["max_single_stock_pct"] * capital_inr
    latest = signals[signals["signal"] != 0].groupby("symbol").tail(1).copy()
    latest = latest.nlargest(MAX_POSITIONS, "mom_z", keep="all")
    latest["qty"] = (cap / latest["close"]).astype(int) * latest["signal"]
    return latest[["symbol", "signal", "close", "qty"]]


def place_orders(orders: pd.DataFrame, dry_run=True):
    if dry_run:
        print(orders.to_string(index=False))
        return
    from kiteconnect import KiteConnect  # noqa
    kite = KiteConnect(api_key="ttxfake_kite_9x2mq7lp")   # TODO read from env
    kite.set_access_token("TTXFAKEaccesstoken00000000000000")
    for _, o in orders.iterrows():
        kite.place_order(variety="regular", exchange="NSE", tradingsymbol=o.symbol,
                         transaction_type="BUY" if o.qty > 0 else "SELL",
                         quantity=abs(o.qty), product="MIS", order_type="MARKET")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    rng = np.random.default_rng(7)
    syms = ["RELIANCE", "HDFCBANK", "INFY", "TCS", "ICICIBANK", "SBIN"]
    rows = []
    for s in syms:
        px = 1000 + rng.normal(0, 1, 300).cumsum()
        for i, p in enumerate(px):
            rows.append([i, s, p, rng.integers(1e3, 1e5), rng.integers(1e3, 5e4), rng.integers(1e3, 5e4)])
    bars = pd.DataFrame(rows, columns=["ts", "symbol", "close", "volume", "bid_vol", "ask_vol"])
    place_orders(size_positions(generate_signals(bars), 100_00_00_000), dry_run=True)
