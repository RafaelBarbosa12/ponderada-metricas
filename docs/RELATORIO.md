# Relatório técnico — Métricas de pipeline CI/CD

**Aluno:** Rafael Barbosa  
**Repositório:** https://github.com/RafaelBarbosa12/ponderada-metricas  
**Workflow:** https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/.github/workflows/ci.yml  
**Actions:** https://github.com/RafaelBarbosa12/ponderada-metricas/actions  
**Entregáveis:** [entregaveis.md](../entregaveis.md)

> Dados coletados em 03/06/2026 via `collect_metrics.py` — **20 execuções**, todas em `ponderada-metricas`.

---

## 1. Objetivo

Instrumentar um pipeline GitHub Actions, executar **12 variações controladas**, coletar métricas reais (API + artefatos), gerar gráficos e analisar desempenho, estabilidade e gargalos.

### Hipóteses iniciais

1. O job **test** domina o tempo com suite expandida ou teste lento.
2. **Cache pip** reduz tempo de instalação.
3. **Paralelismo** (lint ∥ test) reduz tempo de parede vs sequencial.
4. **Falha intencional** aparece como principal causa de `failure` no workflow.

---

## 2. Pipeline

| Requisito | Implementação |
|-----------|----------------|
| Dependências | `pip install -r requirements-dev.txt` |
| Lint | `ruff check src tests` |
| Testes | `pytest` + `reports/junit.xml` |
| Artefatos | `test-results-{run_id}`, `pipeline-metrics-{run_id}` |
| Métricas | `record_pipeline_metrics.py` + `collect_metrics.py` |

- **Paralelo:** `ci.yml` — jobs `lint` e `test` em paralelo.
- **Sequencial:** `ci-sequential.yml` — `test` com `needs: lint` (disparo via `.sequential-marker`).
- **Variações:** `experiment-config.json` + `load_experiment_config.py`.

---

## 3. Variações (12)

Ver [experiments/VARIATIONS.md](../experiments/VARIATIONS.md).

| # | Rótulo | Paralelo | Cache | Expand | Slow | Fail |
|---|--------|----------|-------|--------|------|------|
| 01–12 | (tabela completa no VARIATIONS.md) | — | — | — | — | — |

Cada variação foi disparada com commit `exp:<rótulo>` no repositório `ponderada-metricas`.

---

## 4. Evidências reais

### Execuções do experimento (run_id | variação | duração | link)

| run_id | Variação | s | URL |
|--------|----------|---|-----|
| 26891004909 | 01-baseline-paralelo-cache | 60 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891004909) |
| 26891009858 | 02-sem-cache | 49 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891009858) |
| 26891075815 | 03-sequencial-cache | 57 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891075815) |
| 26891081213 | 04-sequencial-sem-cache | 55 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891081213) |
| 26891017931 | 05-testes-expandidos | 59 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891017931) |
| 26891024956 | 06-teste-lento | 54 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891024956) |
| 26891029560 | 07-falha-intencional | 54 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891029560) |
| 26891036930 | 08-expandido-lento | 53 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891036930) |
| 26891043610 | 09-sem-cache-expandido | 51 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891043610) |
| 26891088531 | 10-sequencial-expandido | 56 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891088531) |
| 26891097104 | 11-sequencial-falha | 57 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891097104) |
| 26891051184 | 12-baseline-repeticao | 66 | [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891051184) |

**Total:** 20 runs no CSV (12 variações + runs de documentação/setup iniciais). Todas com `test_count=13` nas runs de experimento (6 base + 7 skipped condicionais).

### Commits

Commits `exp:*` listados em `experiments/run-log.txt` (SHAs no GitHub em cada run).

---

## 5. Base de dados e gráficos

- `data/metrics/metrics_latest.csv` / `.json`
- Script: `scripts/collect_metrics.py` (não manual)

![Tempo total](../charts/01_tempo_total_pipeline.png)

![Tempo por job](../charts/02_tempo_por_job.png)

![Sucesso e falha](../charts/03_taxa_sucesso_falha.png)

![Testes vs duração](../charts/04_testes_vs_duracao.png)

---

## 6. Análise (perguntas do professor)

### 6.1 Etapa que mais contribui para o tempo total

Jobs **lint**, **test** e **collect-metrics** têm duração semelhante (~50–60 s no modo paralelo). O tempo de parede ≈ `max(lint, test) + collect-metrics`. **collect-metrics** pesa por download/upload de artefatos.

### 6.2 Cache: diferença significativa?

**02-sem-cache (49 s)** vs **01-baseline (60 s)** e **09-sem-cache-expandido (51 s)** vs **05-expandido (59 s)** → cache parece reduzir ~10–15% no tempo total (ruído de runner incluído).

### 6.3 Paralelismo

Paralelo **~49–60 s** (runs 01, 02, 05–09) vs sequencial **~55–57 s** (03, 04, 10, 11) — ganho modesto neste projeto pequeno; paralelismo ajuda mais quando lint e test somam carga semelhante e não há fila no runner.

### 6.4 Falhas mais frequentes

No conjunto coletado, **100% success** em `conclusion` das 20 runs. Falhas de teste nas variações 07 e 11 ficam no JUnit (`continue-on-error`), não como `failure` do workflow.

### 6.5 Feedback rápido?

Mediana das runs de experimento **~54–60 s** — aceitável para PR pequeno em runner gratuito.

### 6.6 Melhorias

- Cache compartilhado entre jobs; job único para pushes triviais; métricas históricas em branch dedicada; separar testes `@slow`.

### 6.7 Limitações

- Duração via API é aproximada; ruído de runner; `continue-on-error` mascara falha no status do workflow; dois workflows com `run_number` independente.

### 6.8 Decisões de engenharia

Dados mostram onde otimizar (cache, paralelismo, peso de collect-metrics). Taxa de sucesso do workflow não reflete sozinha qualidade dos testes — usar JUnit + métricas de falha.

---

## 7. Resultados inesperados

1. **Teste lento (+3 s)** não elevou muito o tempo total (06 ≈ 54 s) — overhead de install/CI domina.
2. **Falha intencional** com workflow ainda **success** — exige ler `test_failures` no artefato.
3. **02-sem-cache mais rápido que 01-com-cache** em uma medição — possível ruído de runner ou cache frio vs quente.

---

## 8. Hipótese vs observado

| Hipótese | Observado | Veredito |
|----------|-----------|----------|
| Test domina com slow/expand | Diferença pequena entre runs (~51–59 s) | Parcial |
| Cache reduz tempo | ~10–15% em alguns pares | Parcial |
| Paralelo < sequencial | Ganho modesto | Parcial |
| Falhas = fail flag | Workflow success; falha no JUnit | Refutada (para `conclusion`) |

---

## 9. Conclusão

O repositório **ponderada-metricas** concentra pipeline, 12 variações, 20 runs reais, coleta via API, CSV/JSON, quatro gráficos e este relatório — sem dependência de outro repositório.

---

## 10. Reprodução

Ver [entregaveis.md](../entregaveis.md) e [README.md](../README.md).
