#!/usr/bin/env bash
# Deploy core-engine to prod jump box (SYNTHETIC - Vault Crimson TTX)
set -e
JUMP=10.42.8.15
SSH_USER=deploy
export PGPASSWORD='Kfl@Prod#2025!TTX'
scp -i ~/.ssh/kfl_prod_deploy.pem -r . ${SSH_USER}@${JUMP}:/opt/kfl-core-engine
ssh -i ~/.ssh/kfl_prod_deploy.pem ${SSH_USER}@${JUMP} "cd /opt/kfl-core-engine && sudo systemctl restart kfl-core"
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"core-engine deployed by '"$USER"'"}' \
  https://hooks.slack.example/services/TTX000/FAKE000/ttxfakewebhooktoken
