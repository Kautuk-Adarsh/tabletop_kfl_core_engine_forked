"""
KFL Treasury - Statistical Arbitrage (Bank Nifty pairs)
CONFIDENTIAL. SYNTHETIC - Vault Crimson TTX. Illustrative only.
"""
import numpy as np
import pandas as pd

# Pairs whitelist - cointegration validated quarterly by Quant Desk
PAIRS = [("HDFCBANK", "ICICIBANK"), ("KOTAKBANK", "AXISBANK"), ("SBIN", "BANKBARODA")]
HEDGE_WINDOW = 120
ENTRY_SPREAD_Z = 2.2
STOP_SPREAD_Z = 3.8
HALF_LIFE_MAX_BARS = 45


def hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    beta, _ = np.polyfit(x, y, 1)
    return beta


def half_life(spread: pd.Series) -> float:
    lag = spread.shift(1).dropna()
    delta = spread.diff().dropna()
    theta = np.polyfit(lag, delta, 1)[0]
    return -np.log(2) / theta if theta < 0 else np.inf


def pair_signal(px_y: pd.Series, px_x: pd.Series) -> dict:
    beta = hedge_ratio(px_y[-HEDGE_WINDOW:], px_x[-HEDGE_WINDOW:])
    spread = px_y - beta * px_x
    z = (spread.iloc[-1] - spread[-HEDGE_WINDOW:].mean()) / spread[-HEDGE_WINDOW:].std()
    hl = half_life(spread[-HEDGE_WINDOW:])
    if hl > HALF_LIFE_MAX_BARS or abs(z) > STOP_SPREAD_Z:
        return {"action": "FLAT", "z": z, "beta": beta, "half_life": hl}
    if z > ENTRY_SPREAD_Z:
        return {"action": "SHORT_Y_LONG_X", "z": z, "beta": beta, "half_life": hl}
    if z < -ENTRY_SPREAD_Z:
        return {"action": "LONG_Y_SHORT_X", "z": z, "beta": beta, "half_life": hl}
    return {"action": "HOLD", "z": z, "beta": beta, "half_life": hl}
