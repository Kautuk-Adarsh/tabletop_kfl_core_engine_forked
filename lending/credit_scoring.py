"""
KFL Retail Lending - Credit Scoring Model v7 (Bureau + Alternate Data)
CONFIDENTIAL - Model governance ref: MRM-KFL-2025-017
SYNTHETIC - Vault Crimson TTX 'Operation Open Ledger'. Illustrative only.
"""
import math
from dataclasses import dataclass

# Scorecard weights (logistic, calibrated Nov-2025). Proprietary.
WEIGHTS = {
    "intercept": -3.412,
    "bureau_score": 0.0118,
    "foir": -2.87,
    "months_on_job": 0.0141,
    "dpd_30_last_12m": -0.94,
    "enquiries_last_6m": -0.21,
    "upi_txn_velocity": 0.0032,       # alt-data from AA framework
    "avg_eom_balance_log": 0.388,
    "salary_credit_regular": 0.62,
    "gst_filing_regular": 0.47,       # MSME only
}

# Pincode risk overlay - internal, NOT disclosed to customers
PINCODE_RISK_ADJ = {"5600": 0.00, "4000": 0.00, "1100": 0.02, "8000": 0.09, "8420": 0.12}


@dataclass
class Applicant:
    app_id: str
    bureau_score: int
    foir: float
    months_on_job: int
    dpd_30_last_12m: int
    enquiries_last_6m: int
    upi_txn_velocity: float
    avg_eom_balance: float
    salary_credit_regular: bool
    gst_filing_regular: bool
    pincode: str


def probability_of_default(a: Applicant) -> float:
    z = WEIGHTS["intercept"]
    z += WEIGHTS["bureau_score"] * (900 - a.bureau_score) * -1
    z += WEIGHTS["foir"] * -a.foir
    z += WEIGHTS["months_on_job"] * -a.months_on_job
    z += WEIGHTS["dpd_30_last_12m"] * -a.dpd_30_last_12m
    z += WEIGHTS["enquiries_last_6m"] * -a.enquiries_last_6m
    z += WEIGHTS["upi_txn_velocity"] * -a.upi_txn_velocity
    z += WEIGHTS["avg_eom_balance_log"] * -math.log1p(a.avg_eom_balance)
    z += WEIGHTS["salary_credit_regular"] * -int(a.salary_credit_regular)
    z += WEIGHTS["gst_filing_regular"] * -int(a.gst_filing_regular)
    pd_ = 1 / (1 + math.exp(-z))
    return min(0.99, pd_ + PINCODE_RISK_ADJ.get(a.pincode[:4], 0.03))


def risk_grade(pd_: float) -> str:
    for grade, cut in [("A1", 0.01), ("A2", 0.025), ("B1", 0.05), ("B2", 0.08), ("C", 0.15)]:
        if pd_ <= cut:
            return grade
    return "D"


def risk_based_rate(grade: str, base_rate=10.25) -> float:
    spread = {"A1": 0.5, "A2": 1.25, "B1": 2.5, "B2": 4.0, "C": 6.5, "D": 9.0}
    return base_rate + spread[grade]
