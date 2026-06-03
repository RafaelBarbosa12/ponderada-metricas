#!/usr/bin/env bash
# Dispara runs sequenciais via API (sem gh CLI)
set -euo pipefail

REPO="${1:-RafaelBarbosa12/ponderada-metricas}"
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
API="https://api.github.com/repos/${REPO}/actions/workflows/ci-sequential.yml/dispatches"

if [ -z "$TOKEN" ]; then
  echo "Defina GITHUB_TOKEN para disparar workflows sequenciais."
  exit 1
fi

dispatch() {
  local label="$1" cache="$2" expand="$3" slow="$4" fail="$5"
  curl -sS -X POST "$API" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -d "{\"ref\":\"main\",\"inputs\":{\"experiment_variation\":\"$label\",\"cache_enabled\":$cache,\"expand_tests\":$expand,\"run_slow_tests\":$slow,\"intentional_fail\":$fail}}"
  echo " -> $label"
  sleep 8
}

dispatch "03-sequencial-cache" true false false false
dispatch "04-sequencial-sem-cache" false false false false
dispatch "10-sequencial-expandido" true true false false
dispatch "11-sequencial-falha" true false false true

echo "4 workflows sequenciais disparados."
