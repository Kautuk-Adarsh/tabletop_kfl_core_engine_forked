# kfl-core-engine

Core decisioning services for **Kaveri Finserv Ltd (KFL)** — Treasury, Lending & Customer Analytics.

> ⚠️ **SYNTHETIC TRAINING ARTEFACT — Vault Crimson Series TTX "Operation Open Ledger" by FlexibleIR.**
> Kaveri Finserv Ltd is a fictional entity. All code, logic, customers, credentials and keys in this
> repository are fabricated and non-functional. See `DRILL_NOTICE.md`.

## Modules
| Module | Purpose | Owner team |
|---|---|---|
| `trading/` | Intraday momentum + stat-arb pairs strategies, pre-trade risk limits | Treasury Quant Desk |
| `lending/` | Credit scoring (bureau + alt-data) and loan disbursal engine | Retail Lending Tech |
| `customer/` | Customer segmentation, KYC risk rating, cross-sell propensity | Customer Analytics |
| `decisioning/` | Rules engine for pricing, approvals, collections priority | Decision Sciences |
| `infra/` | Terraform for AWS ap-south-1 workloads | Platform |

## Local setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config/.env.example .env   # (we just use config/.env for now - arjun)
python -m trading.momentum_strategy --dry-run
```

## Internal contacts
- Treasury Quant: quant-desk@kaverifinserv.example
- Lending Tech: lending-eng@kaverifinserv.example
