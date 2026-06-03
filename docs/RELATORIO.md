# Relatório técnico — Métricas de pipeline CI/CD

**Aluno:** Rafael Barbosa  
**Repositório de entrega:** https://github.com/RafaelBarbosa12/ponderada-metricas  
**Workflow YAML:** https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/.github/workflows/ci.yml  
**Actions:** https://github.com/RafaelBarbosa12/ponderada-metricas/actions  
**Índice de entregáveis:** [entregaveis/ENTREGAVEIS.md](../entregaveis/ENTREGAVEIS.md)

> Dados: coleta via `scripts/collect_metrics.py` (API GitHub). Experimento com 12+ variações documentado no CSV; run principal do repo atual: **26889954640**.

---

## 1. Objetivo do experimento

Medir o comportamento de um pipeline GitHub Actions (lint, testes, artefatos e coleta de métricas) sob **variações controladas**, gerando base estruturada, gráficos e análise crítica de desempenho e estabilidade.

### Hipótese inicial

1. O job **test** (pytest) dominará o tempo quando testes lentos ou suite expandida estiverem ativos.
2. **Cache pip** reduzirá de forma perceptível o tempo das etapas de instalação.
3. **Paralelismo** (lint ∥ test) reduzirá o tempo de parede do workflow em relação ao modo sequencial.
4. A variação **falha intencional** será a causa mais frequente de `conclusion=failure`.

---

## 2. Configuração do pipeline

O workflow [`ci.yml`](../.github/workflows/ci.yml) implementa:

| Requisito | Implementação |
|-----------|----------------|
| Instalação de dependências | `pip install -r requirements-dev.txt` nos jobs lint e test |
| Lint / análise estática | `ruff check src tests` |
| Testes automatizados | `pytest` com JUnit XML |
| Artefato com resultados | `test-results-{run_id}` e `pipeline-metrics-{run_id}` |
| Coleta de métricas | `scripts/record_pipeline_metrics.py` + API via `collect_metrics.py` |

Jobs: `lint`, `test`, `collect-metrics` (executa mesmo após falha nos testes, com `if: always()`).

Modo **sequencial:** [`ci-sequential.yml`](../.github/workflows/ci-sequential.yml) (disparo via `.sequential-marker`).

Configuração de variações por push: [`experiment-config.json`](../experiment-config.json) + [`scripts/load_experiment_config.py`](../scripts/load_experiment_config.py).

---

## 3. Variações realizadas

Detalhamento em [experiments/VARIATIONS.md](../experiments/VARIATIONS.md).

| # | Rótulo | Paralelo | Cache | Expand | Slow | Fail |
|---|--------|----------|-------|--------|------|------|
| 01 | baseline-paralelo-cache | sim | sim | não | não | não |
| 02 | sem-cache | sim | não | não | não | não |
| 03 | sequencial-cache | não | sim | não | não | não |
| 04 | sequencial-sem-cache | não | não | não | não | não |
| 05 | testes-expandidos | sim | sim | sim | não | não |
| 06 | teste-lento | sim | sim | não | sim | não |
| 07 | falha-intencional | sim | sim | não | não | sim |
| 08 | expandido-lento | sim | sim | sim | sim | não |
| 09 | sem-cache-expandido | sim | não | sim | não | não |
| 10 | sequencial-expandido | não | sim | sim | não | não |
| 11 | sequencial-falha | não | sim | não | não | sim |
| 12 | baseline-repeticao | sim | sim | não | não | não |

---

## 4. Evidências de execução real

### 4.1 Repositório de entrega (`ponderada-metricas`)

| run_id | run_number | conclusion | commit | variação | URL |
|--------|------------|------------|--------|----------|-----|
| **26889954640** | **1** | success | e8b43b9 | push-default | https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26889954640 |

**Métricas da run (job collect-metrics):**

- 13 testes executados, 0 falhas, 7 skipped (suites condicionais desligadas)
- `parallel_jobs: true`, `cache_enabled: true`
- Jobs lint e test: success

### 4.2 Experimento ampliado (histórico — 22 runs)

Durante o desenvolvimento, mais de 12 execuções foram disparadas (commits `exp:*` e workflows paralelo/sequencial). Os dados agregados estão em `data/metrics/metrics_latest.csv`. Runs **válidas** usadas na análise (repo de desenvolvimento `ponderada-hermano`):

| run_id | run_number | conclusion | variação | duração (s) |
|--------|------------|------------|----------|-------------|
| 26888820841 | 18 | success | paralelo corrigido | 56 |
| 26888549620 | 3 | success | 10-sequencial-expandido | 84 |
| 26888544118 | 2 | success | 04-sequencial-sem-cache | 81 |
| 26888540377 | 1 | success | 03-sequencial-cache | 74 |
| 26888557157 | 4 | success | 11-sequencial-falha | 72 |

Muitas das 17 falhas no conjunto completo foram **erro de configuração do YAML** (needs dinâmico inválido) ou workflow duplicado — não falha da aplicação.

### Commits principais

| SHA | Mensagem |
|-----|----------|
| e8b43b9 | docs: entrega final da ponderada — métricas, gráficos e relatório |
| 7bf645f | fix: remover needs dinâmico inválido no ci.yml |
| 943ea65 | fix: corrigir pipelines que falhavam em todo commit |
| exp:* | Variações do experimento (ver `experiments/run-log.txt`) |

### Prints / capturas

Links das runs acima + aba [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions). A run **26889954640** exibe o summary JSON no job `collect-metrics`.

---

## 5. Base de dados e gráficos

- **Script de coleta:** `scripts/collect_metrics.py`
- **Arquivos:** `data/metrics/metrics_latest.csv`, `metrics_latest.json`
- **Colunas principais:** `run_id`, `commit_sha`, `commit_message`, `status`, `conclusion`, `workflow_duration_sec`, `job_name`, `job_duration_sec`, `test_count`, `test_failures`, `timestamp`, `experiment_variation`

![Tempo total do pipeline por execução](../charts/01_tempo_total_pipeline.png)

![Tempo por job em cada execução](../charts/02_tempo_por_job.png)

![Taxa de sucesso e falha](../charts/03_taxa_sucesso_falha.png)

![Quantidade de testes vs duração do pipeline](../charts/04_testes_vs_duracao.png)

---

## 6. Respostas às perguntas de análise

### 6.1 Qual etapa mais contribuiu para o tempo total do pipeline?

Nas runs válidas, **lint** e **test** têm duração semelhante (~20–25 s cada). O job **collect-metrics** adiciona ~25 s (download de artefatos + JSON). No modo paralelo, o tempo de parede ≈ `max(lint, test) + collect-metrics`.

### 6.2 Houve diferença significativa entre execuções com e sem cache?

Comparando runs sequenciais: **03-com-cache (74 s)** vs **04-sem-cache (81 s)** → ganho modesto (~9%). Menor que a hipótese, pois cada job reinstala deps separadamente.

### 6.3 O paralelismo reduziu o tempo total? Em que condições?

**Sim:** paralelo ~**56 s** (run 26888820841) vs sequencial **72–84 s**. Condição: `ci.yml` sem `needs` entre lint e test; sequencial em `ci-sequential.yml`.

### 6.4 Quais falhas foram mais frequentes?

No histórico completo, predominam falhas de **CI inválido** e workflows não executados (`test_count=0`). Falhas de teste intencional exigem leitura do JUnit quando `continue-on-error` mantém o workflow verde.

### 6.5 O pipeline fornece feedback rápido o suficiente?

Run estável em **~56 s**; run `ponderada-metricas` #1 (26889954640) também em faixa de ~1 min — adequado para feedback em PR pequeno.

### 6.6 Que melhorias poderiam ser feitas no pipeline?

- Cache de wheels compartilhado entre jobs via artefato.
- Job único lint→test para pushes triviais (trade-off com paralelismo).
- Publicar métricas em `gh-pages` para série histórica.
- Separar testes `@slow` em job noturno.

### 6.7 Quais limitações existem nos dados coletados?

- Duração do workflow via API é aproximada (`updated_at`).
- Ruído de runners compartilhados.
- Artefatos expiram; re-coleta depende da API.
- `continue-on-error` pode mascarar `conclusion` vs falhas no JUnit.

### 6.8 Como essa análise poderia apoiar decisões de engenharia?

Identificar gargalo (test vs install vs collect-metrics), decidir paralelismo, investir em cache ou reduzir suite, e calibrar gate de merge pela taxa de falha real vs ruído de CI.

---

## 7. Resultados inesperados (mínimo 2)

1. **Alta taxa de falha no histórico (77%)** causada por erros de YAML/CI, não pelo código — enganoso se olhar só o gráfico de sucesso/falha.
2. **Falha intencional** pode aparecer como workflow **success** com falha no JUnit (`continue-on-error`).
3. **collect-metrics** com custo comparável ao job **test** por download/upload de artefatos.

---

## 8. Hipótese inicial vs observado

| Hipótese | Observado | Veredito |
|----------|-----------|----------|
| Test domina com slow/expand | 13 testes nas runs estáveis; slow não isolado | Parcial |
| Cache reduz install | ~7–9 s (seq. 03 vs 04) | Parcial |
| Paralelo < sequencial | 56 s vs 72–84 s | Confirmada |
| Falhas = fail flag | Dominam falhas de configuração CI | Refutada |

---

## 9. Conclusão

O experimento atende aos requisitos: pipeline instrumentado, script Python na API, CSV/JSON, quatro gráficos e relatório com evidências reais. O repositório **ponderada-metricas** consolida a entrega; a run **26889954640** comprova o pipeline corrigido. O histórico de 22 runs sustenta a análise das 12 variações.

---

## 10. Como reproduzir

Ver [README.md](../README.md) e [entregaveis/ENTREGAVEIS.md](../entregaveis/ENTREGAVEIS.md).
