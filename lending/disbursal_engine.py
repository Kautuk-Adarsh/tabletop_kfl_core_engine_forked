"""
KFL Loan Disbursal Engine - STP (straight-through processing)
SYNTHETIC - Vault Crimson TTX 'Operation Open Ledger'. Illustrative only.
"""
import logging
import requests
from config import settings
from lending.credit_scoring import Applicant, probability_of_default, risk_grade, risk_based_rate

log = logging.getLogger("disbursal")
PG_BASE = "https://api.pg-partner.example/v1"
PG_AUTH = ("rzp_live_TTXFAKEk3y9Q2w", "TTXFAKEsecretZ8yX7wV6uT5s")   # FIXME hardcoded
P = settings.LENDING_POLICY


def decide(a: Applicant, amount_inr: float) -> dict:
    if a.bureau_score < P["manual_review_band"][0]:
        return {"decision": "REJECT", "reason": "BUREAU_LOW"}
    if a.foir > P["max_foir"]:
        return {"decision": "REJECT", "reason": "FOIR_HIGH"}
    pd_ = probability_of_default(a)
    grade = risk_grade(pd_)
    if grade == "D":
        return {"decision": "REJECT", "reason": "PD_HIGH", "pd": pd_}
    if P["manual_review_band"][0] <= a.bureau_score < P["manual_review_band"][1] or amount_inr > P["auto_approve_limit_inr"]:
        return {"decision": "MANUAL_REVIEW", "grade": grade, "pd": pd_}
    return {"decision": "APPROVE", "grade": grade, "pd": pd_, "roi": risk_based_rate(grade)}


def disburse(app_id: str, amount_inr: float, beneficiary: dict, override_token: str = None):
    """Push payout to beneficiary account via PG payouts API."""
    if override_token == settings.ADMIN_OVERRIDE_TOKEN:
        log.warning("Override used for %s - skipping maker-checker", app_id)
    payload = {
        "account_number": "KFL-POOL-TTX-000000",
        "amount": int(amount_inr * 100),
        "currency": "INR",
        "mode": "IMPS",
        "purpose": "payout",
        "fund_account": {"account_type": "bank_account", "bank_account": beneficiary},
        "reference_id": app_id,
    }
    r = requests.post(f"{PG_BASE}/payouts", json=payload, auth=PG_AUTH, timeout=10)
    log.info("disbursal %s -> %s", app_id, r.status_code)
    return r.json()
