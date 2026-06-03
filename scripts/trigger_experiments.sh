#!/usr/bin/env bash
# Dispara 12+ execuções do workflow com variações controladas.
# Requer: gh auth login
set -euo pipefail

REPO="${1:-RafaelBarbosa12/ponderada-metricas}"

dispatch() {
  local label="$1"
  local parallel="$2"
  local cache="$3"
  local expand="$4"
  local slow="$5"
  local fail="$6"
  echo ">>> Disparando: $label"
  gh workflow run ci.yml \
    --repo "$REPO" \
    -f "experiment_variation=$label" \
    -f "parallel_jobs=$parallel" \
    -f "cache_enabled=$cache" \
    -f "expand_tests=$expand" \
    -f "run_slow_tests=$slow" \
    -f "intentional_fail=$fail"
  sleep 8
}

dispatch "01-baseline-paralelo-cache" true true false false false
dispatch "02-sem-cache" true false false false false
dispatch "03-sequencial-cache" false true false false false
dispatch "04-sequencial-sem-cache" false false false false false
dispatch "05-testes-expandidos" true true true false false
dispatch "06-teste-lento" true true false true false
dispatch "07-falha-intencional" true true false false true
dispatch "08-expandido-lento" true true true true false
dispatch "09-sem-cache-expandido" true false true false false
dispatch "10-sequencial-expandido" false true true false false
dispatch "11-sequencial-falha" false true false false true
dispatch "12-baseline-repeticao" true true false false false

echo ""
echo "12 workflows disparados. Acompanhe em:"
echo "https://github.com/$REPO/actions"
echo "Após concluírem, rode:"
echo "  export GITHUB_TOKEN=\$(gh auth token)"
echo "  python scripts/collect_metrics.py"
echo "  python scripts/generate_charts.py"
