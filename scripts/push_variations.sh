#!/usr/bin/env bash
# Cria 12 commits (cada um dispara o workflow em ci.yml no push)
set -euo pipefail

cd "$(dirname "$0")/.."

configs=(
  '01-baseline-paralelo-cache|true|true|false|false|false'
  '02-sem-cache|true|false|false|false|false'
  '05-testes-expandidos|true|true|true|false|false'
  '06-teste-lento|true|true|false|true|false'
  '08-expandido-lento|true|true|true|true|false'
  '09-sem-cache-expandido|true|false|true|false|false'
  '12-baseline-repeticao|true|true|false|false|false'
)

for entry in "${configs[@]}"; do
  IFS='|' read -r label parallel cache expand slow fail <<< "$entry"
  cat > experiment-config.json <<EOF
{
  "experiment_variation": "$label",
  "parallel_jobs": $parallel,
  "cache_enabled": $cache,
  "expand_tests": $expand,
  "run_slow_tests": $slow,
  "intentional_fail": $fail
}
EOF
  echo "$label $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> experiments/run-log.txt
  git add experiment-config.json experiments/run-log.txt
  git commit -m "exp:$label — variação do experimento CI/CD" --allow-empty
  git push origin main
  echo "Pushed $label"
  sleep 5
done

echo ""
echo "8 runs paralelas disparadas via push."
echo "Para runs 03,04,10,11 (sequenciais), use workflow_dispatch em ci-sequential.yml"
echo "ou instale gh e rode scripts/trigger_experiments.sh"
