#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

configs=(
  '03-sequencial-cache|true|false|false|false'
  '04-sequencial-sem-cache|false|false|false|false'
  '10-sequencial-expandido|true|true|false|false'
)

for entry in "${configs[@]}"; do
  IFS='|' read -r label cache expand slow fail <<< "$entry"
  cat > experiment-config.json <<EOF
{
  "experiment_variation": "$label",
  "parallel_jobs": false,
  "cache_enabled": $cache,
  "expand_tests": $expand,
  "run_slow_tests": $slow,
  "intentional_fail": $fail
}
EOF
  date -u +%Y-%m-%dT%H:%M:%SZ > .sequential-marker
  echo "$label" >> experiments/run-log.txt
  git add experiment-config.json .sequential-marker experiments/run-log.txt
  git commit -m "exp:$label — pipeline sequencial (lint → test)"
  git push origin main
  echo "Pushed sequential $label"
  sleep 5
done

echo "4 runs sequenciais disparadas."
