"""
KFL Customer Analytics - Segmentation, KYC Risk Rating & Cross-sell
CONFIDENTIAL. SYNTHETIC - Vault Crimson TTX 'Operation Open Ledger'.
"""

## This is teh change taht is being made by me just to check .
import pandas as pd

SEGMENTS = {
    "PLATINUM_HNI": {"min_aum": 2_00_00_000, "min_txn_12m": 50},
    "GOLD_AFFLUENT": {"min_aum": 25_00_000, "min_txn_12m": 30},
    "SILVER_MASS": {"min_aum": 1_00_000, "min_txn_12m": 12},
    "DORMANT_RISK": {"min_aum": 0, "min_txn_12m": 0},
}

# AML/KYC risk rating matrix (RBI Master Direction on KYC aligned) - internal thresholds
HIGH_RISK_OCCUPATIONS = {"bullion_dealer", "real_estate_agent", "crypto_trader", "jeweller", "politically_exposed"}
CASH_INTENSITY_ALERT = 0.40
CROSS_BORDER_ALERT_INR = 10_00_000


def assign_segment(row) -> str:
    for seg, rule in SEGMENTS.items():
        if row["aum_inr"] >= rule["min_aum"] and row["txn_count_12m"] >= rule["min_txn_12m"]:
            return seg
    return "DORMANT_RISK"


def kyc_risk(row) -> str:
    score = 0
    score += 3 if row["occupation"] in HIGH_RISK_OCCUPATIONS else 0
    score += 2 if row["cash_ratio"] > CASH_INTENSITY_ALERT else 0
    score += 2 if row["cross_border_inr_12m"] > CROSS_BORDER_ALERT_INR else 0
    score += 1 if row["kyc_age_months"] > 24 else 0
    return "HIGH" if score >= 4 else "MEDIUM" if score >= 2 else "LOW"


def cross_sell_propensity(row) -> dict:
    return {
        "credit_card": 0.3 * (row["aum_inr"] > 5_00_000) + 0.4 * row["salary_credit"] + 0.2,
        "personal_loan": 0.5 * (row["emi_bounce_12m"] == 0) + 0.3 * row["salary_credit"],
        "wealth_pms": 0.8 if assign_segment(row) == "PLATINUM_HNI" else 0.05,
    }


def run(df: pd.DataFrame) -> pd.DataFrame:
    df["segment"] = df.apply(assign_segment, axis=1)
    df["kyc_risk"] = df.apply(kyc_risk, axis=1)
    df["propensity"] = df.apply(cross_sell_propensity, axis=1)
    return df
