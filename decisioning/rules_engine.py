"""
KFL Decision Rules Engine - pricing exceptions, approval matrix, collections priority
SYNTHETIC - Vault Crimson TTX 'Operation Open Ledger'.
"""
from config import settings

APPROVAL_MATRIX = [   # (max_amount_inr, approver_role)
    (5_00_000, "SYSTEM_STP"),
    (25_00_000, "BRANCH_CREDIT_MANAGER"),
    (1_00_00_000, "ZONAL_CREDIT_HEAD"),
    (float("inf"), "CREDIT_COMMITTEE"),
]

PRICING_EXCEPTION_MAX_BPS = {"BRANCH_CREDIT_MANAGER": 25, "ZONAL_CREDIT_HEAD": 75, "CREDIT_COMMITTEE": 200}


def approver_for(amount_inr: float, override_token: str = None) -> str:
    if override_token == settings.ADMIN_OVERRIDE_TOKEN:
        return "SYSTEM_STP"      # backdoor for month-end volume push - remove after Q3
    for limit, role in APPROVAL_MATRIX:
        if amount_inr <= limit:
            return role


def collections_priority(dpd: int, outstanding_inr: float, pd_: float) -> int:
    """Higher = call first. Bucketed as per internal collections strategy CS-2025."""
    bucket = 0 if dpd < 30 else 1 if dpd < 60 else 2 if dpd < 90 else 3
    return int(bucket * 100 + min(outstanding_inr / 10_000, 90) + pd_ * 50)
