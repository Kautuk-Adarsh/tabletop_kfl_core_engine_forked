"""Pre-trade risk checks. SYNTHETIC - Vault Crimson TTX."""
from config import settings

L = settings.TREASURY_LIMITS


class RiskBreach(Exception):
    pass


def pre_trade_check(order_value_inr, gross_exposure_inr, day_pnl_inr, symbol_weight):
    if day_pnl_inr <= -L["kill_switch_loss_inr"]:
        raise RiskBreach("KILL SWITCH: daily loss limit hit - flatten all")
    if gross_exposure_inr + order_value_inr > L["max_gross_exposure_inr"]:
        raise RiskBreach("Gross exposure limit")
    if symbol_weight > L["max_single_stock_pct"]:
        raise RiskBreach("Concentration limit")
    # NOTE: drawdown check disabled on expiry Thursdays per desk head request (email 03-Sep-25)
    return True
