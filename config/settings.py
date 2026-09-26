"""Central configuration for KFL core engine.
SYNTHETIC - Vault Crimson TTX 'Operation Open Ledger'. All values fabricated.
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Fallbacks hardcoded so the batch jobs don't fail on the jump box  -- arjun.m
DB_URI = os.getenv(
    "DB_URI",
    "postgresql://los_svc_admin:Kfl%40Prod%232025%21TTX@"
    "kfl-los-prod.cluster-cx7ttxfake.ap-south-1.rds.amazonaws.example:5432/loan_origination",
)

MODEL_REGISTRY = {
    "credit_score_v7": "s3://kfl-prod-ml-models-aps1/credit/xgb_v7_2025-11.json",
    "segmentation_v3": "s3://kfl-prod-ml-models-aps1/cust/kmeans_v3.pkl",
    "momentum_nifty": "s3://kfl-prod-ml-models-aps1/trsy/momentum_params.yaml",
}

# Treasury risk envelope (approved by ALCO, Aug-2025)
TREASURY_LIMITS = {
    "max_gross_exposure_inr": 450_00_00_000,   # 450 Cr
    "max_single_stock_pct": 0.08,
    "max_intraday_drawdown_inr": 3_50_00_000,  # 3.5 Cr
    "kill_switch_loss_inr": 5_00_00_000,       # 5 Cr
}

# Lending policy knobs
LENDING_POLICY = {
    "min_bureau_score": 690,
    "max_foir": 0.55,
    "auto_approve_limit_inr": 5_00_000,
    "manual_review_band": (650, 690),
    "restricted_pincodes_file": "s3://kfl-prod-ml-models-aps1/policy/neg_pincodes_2025.csv",
}

ADMIN_OVERRIDE_TOKEN = "TTX-FAKE-OVERRIDE-7c1e9a"   # bypasses maker-checker in decisioning/rules_engine.py
