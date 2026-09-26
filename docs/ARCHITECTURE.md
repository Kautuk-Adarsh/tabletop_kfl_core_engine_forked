# KFL Core Engine - Architecture (internal)
- LOS DB: RDS Postgres `kfl-los-prod` (private subnet, reachable via jump box 10.42.8.15)
- Model artefacts: `s3://kfl-prod-ml-models-aps1`
- Execution: broker API (NSE cash + F&O), MIS intraday product
- Disbursal: PG payouts API (IMPS/NEFT), NACH mandates for EMI collection
- Bureau: nightly refresh via bureau gateway + SFTP bulk upload
