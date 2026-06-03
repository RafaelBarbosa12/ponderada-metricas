# Relatório técnico — Métricas de pipeline CI/CD

**Aluno:** Rafael Barbosa  
**Repositório:** https://github.com/RafaelBarbosa12/ponderada-hermano  
**Workflow YAML:** https://github.com/RafaelBarbosa12/ponderada-hermano/blob/main/.github/workflows/ci.yml  
**Actions (execuções):** https://github.com/RafaelBarbosa12/ponderada-hermano/actions  

> Após rodar `collect_metrics.py`, substitua as seções marcadas com `[PREENCHER]` pelos valores do seu `data/metrics/metrics_latest.csv`.

---

## 1. Objetivo do experimento

Medir o comportamento de um pipeline GitHub Actions (lint, testes, artefatos e coleta de métricas) sob **12 variações controladas**, gerando base estruturada, gráficos e análise crítica de desempenho e estabilidade.

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

Jobs: `lint`, `test`, `collect-metrics` (sempre executa, mesmo após falha nos testes).

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

### Links das runs

[PREENCHER: colar tabela gerada após coleta — exemplo]

| run_id | run_number | conclusion | commit (curto) | variação | URL |
|--------|------------|------------|----------------|----------|-----|
| … | … | … | … | … | https://github.com/RafaelBarbosa12/ponderada-hermano/actions/runs/… |

### Commits utilizados

[PREENCHER: `commit_sha` e `commit_message` do CSV]

### Prints / capturas

Incluir screenshots da aba Actions com pelo menos 3 runs visíveis (IDs legíveis), ou os links acima (aceitos como evidência pelo professor quando IDs são reais).

---

## 5. Base de dados e gráficos

- **Script de coleta:** `scripts/collect_metrics.py` (API GitHub — não é cópia manual)
- **Arquivo:** `data/metrics/metrics_latest.csv`
- **Gráficos:**
  - `charts/01_tempo_total_pipeline.png`
  - `charts/02_tempo_por_job.png`
  - `charts/03_taxa_sucesso_falha.png`
  - `charts/04_testes_vs_duracao.png`

---

## 6. Respostas às perguntas de análise

### 6.1 Qual etapa mais contribuiu para o tempo total do pipeline?

[PREENCHER com base no gráfico 02 e colunas `step_duration_sec` / `job_duration_sec`.]

Em geral, espera-se que **Executar testes** e, na variação 06/08, o marcador `slow` dominem; **Instalar dependências** ganha peso quando `cache_enabled=false`.

### 6.2 Houve diferença significativa entre execuções com e sem cache?

Comparar runs 01 vs 02 e 05 vs 09. [PREENCHER valores médios de duração das steps de install.]

### 6.3 O paralelismo reduziu o tempo total? Em que condições?

Comparar 01 vs 03 e 05 vs 10. O tempo de parede do workflow deve cair quando lint e test sobrepõem, exceto se o runner estiver ocioso em sequencial por espera explícita (`needs: lint`).

### 6.4 Quais falhas foram mais frequentes?

Runs 07 e 11 (`intentional_fail`) devem aparecer como `failure` por assert no pytest. [PREENCHER contagem do gráfico 03.]

### 6.5 O pipeline fornece feedback rápido o suficiente?

Considerar mediana do `workflow_duration_sec` nas runs baseline (< 2–3 min é aceitável em runner gratuito). [PREENCHER mediana.]

### 6.6 Que melhorias poderiam ser feitas no pipeline?

- Cache único compartilhado entre jobs via artefato de wheels.
- Falhar rápido: lint antes de test em um único job para pushes triviais (trade-off vs paralelismo).
- Publicar métricas em branch `gh-pages` ou S3 para histórico longitudinal.
- Matrix de versões Python só quando necessário.

### 6.7 Quais limitações existem nos dados coletados?

- Duração do workflow usa `updated_at` da API (aproximação, não billing exato).
- Runners compartilhados introduzem ruído entre execuções.
- Artefatos expiram; re-coleta depende de API ainda disponível.
- Steps com `continue-on-error` podem marcar sucesso parcial confuso.

### 6.8 Como essa análise poderia apoiar decisões de engenharia?

Priorizar otimização onde os gráficos mostram concentración de tempo (ex.: testes lentos → paralelizar suite ou marcar `@slow` em job noturno). Taxa de falha guia confiabilidade do gate de merge.

---

## 7. Resultados inesperados (mínimo 2)

1. **[PREENCHER]** Ex.: run baseline mais lenta que run sem cache por ruído do runner.
2. **[PREENCHER]** Ex.: job `collect-metrics` com duração comparável ao `test` por download de artefatos.

---

## 8. Hipótese inicial vs observado

| Hipótese | Observado | Veredito |
|----------|-----------|----------|
| Test domina com slow/expand | [PREENCHER] | [confirmada/parcial/refutada] |
| Cache reduz install | [PREENCHER] | … |
| Paralelo < sequencial (parede) | [PREENCHER] | … |
| Falhas concentradas em fail flag | [PREENCHER] | … |

---

## 9. Conclusão

O experimento cumpre a coleta automatizada via script Python, gera CSV/JSON e quatro gráficos a partir de execuções reais no GitHub Actions. [PREENCHER síntese numérica após coleta.]

---

## 10. Como reproduzir

Ver [README.md](../README.md).
