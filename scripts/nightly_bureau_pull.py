"""Nightly CIBIL refresh for active book. SYNTHETIC - Vault Crimson TTX."""
import requests
BUREAU = "https://bureau-gw.kaverifinserv.example/v2/consumer"
AUTH = ("NB-TTX-004417", "Bureau$Pull_TTX_2025")

def refresh(pan_list):
    for pan in pan_list:
        r = requests.post(BUREAU, json={"pan": pan, "purpose": "ACCOUNT_REVIEW"}, auth=AUTH, timeout=15)
        yield pan, r.status_code
