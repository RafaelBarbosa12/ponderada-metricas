# Variações do experimento (12+ execuções)

| # | Variação | Como reproduzir | O que muda |
|---|----------|-----------------|------------|
| 01 | Baseline paralelo + cache | `workflow_dispatch` ou commit normal | lint ∥ test, cache pip |
| 02 | Sem cache | `cache_enabled=false` | install mais lento |
| 03 | Sequencial + cache | `parallel_jobs=false` | test só após lint |
| 04 | Sequencial sem cache | ambos false | maior tempo total esperado |
| 05 | Testes expandidos | `expand_tests=true` | +5 testes |
| 06 | Teste lento | `run_slow_tests=true` | +3s no pytest |
| 07 | Falha intencional | `intentional_fail=true` | pipeline falha nos testes |
| 08 | Expandido + lento | expand + slow | mais testes e sleep |
| 09 | Sem cache + expandido | cache off + expand | install + mais testes |
| 10 | Sequencial expandido | sequential + expand | ordem jobs + suite |
| 11 | Sequencial + falha | sequential + fail | falha após lint |
| 12 | Repetição baseline | igual 01 | estabilidade / ruído |

Disparo em lote:

```bash
chmod +x scripts/trigger_experiments.sh
./scripts/trigger_experiments.sh
```

Commits com prefixo `exp:` também etiquetam a variação (ex.: `exp:05-testes-expandidos`).
