# Entregáveis — Ponderada CI/CD (métricas de pipeline)

**Aluno:** Rafael Barbosa  
**Repositório:** https://github.com/RafaelBarbosa12/ponderada-metricas  
**Actions:** https://github.com/RafaelBarbosa12/ponderada-metricas/actions  
**Data:** 03/06/2026  

---

## 1. Links para o professor

| Item | Link |
|------|------|
| Repositório | https://github.com/RafaelBarbosa12/ponderada-metricas |
| Workflow paralelo (YAML) | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/.github/workflows/ci.yml |
| Workflow sequencial (YAML) | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/.github/workflows/ci-sequential.yml |
| Script coleta (API) | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/scripts/collect_metrics.py |
| Script gráficos | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/scripts/generate_charts.py |
| CSV métricas | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/data/metrics/metrics_latest.csv |
| JSON métricas | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/data/metrics/metrics_latest.json |
| Relatório técnico | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/docs/RELATORIO.md |
| Este arquivo | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/entregaveis.md |

---

## 2. Experimento: 12 variações + 20 execuções reais

Todas as runs abaixo são do repositório **ponderada-metricas** (coletadas via `collect_metrics.py` em 03/06/2026).

### Variações do experimento (commits `exp:`)

| # | Variação | Workflow | run_id (exemplo) | conclusion | duração (s) |
|---|----------|----------|------------------|------------|-------------|
| 01 | baseline-paralelo-cache | CI/CD Métricas | 26891004909 | success | 60 |
| 02 | sem-cache | CI/CD Métricas | 26891009858 | success | 49 |
| 03 | sequencial-cache | CI/CD Métricas (sequencial) | 26891075815 | success | 57 |
| 04 | sequencial-sem-cache | CI/CD Métricas (sequencial) | 26891081213 | success | 55 |
| 05 | testes-expandidos | CI/CD Métricas | 26891017931 | success | 59 |
| 06 | teste-lento | CI/CD Métricas | 26891024956 | success | 54 |
| 07 | falha-intencional | CI/CD Métricas | 26891029560 | success* | 54 |
| 08 | expandido-lento | CI/CD Métricas | 26891036930 | success | 53 |
| 09 | sem-cache-expandido | CI/CD Métricas | 26891043610 | success | 51 |
| 10 | sequencial-expandido | CI/CD Métricas (sequencial) | 26891088531 | success | 56 |
| 11 | sequencial-falha | CI/CD Métricas (sequencial) | 26891097104 | success* | 57 |
| 12 | baseline-repeticao | CI/CD Métricas | 26891051184 | success | 66 |

\* Workflow verde com `continue-on-error`; falha registrada no JUnit (`test_failures` no artefato).

**Total coletado:** 20 workflow runs (12 variações + runs iniciais de setup/docs).

### Links diretos (amostra)

- https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891004909 (01 baseline)
- https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891009858 (02 sem cache)
- https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891029560 (07 falha intencional)
- https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26891075815 (03 sequencial)

Lista completa: aba [Actions](https://github.com/RafaelBarbosa12/ponderada-metricas/actions).

---

## 3. Métricas mínimas (CSV)

Arquivo: `data/metrics/metrics_latest.csv` — gerado por `scripts/collect_metrics.py` (API GitHub + artefatos).

Colunas incluídas: `run_id`, `commit_sha`, `commit_message`, `status`, `conclusion`, `workflow_duration_sec`, `job_name`, `job_duration_sec`, `step_name`, `step_duration_sec`, `test_count`, `test_failures`, `test_time_avg_sec`, `timestamp`, `experiment_variation`, `parallel_jobs`, `cache_enabled`, etc.

---

## 4. Gráficos (4 obrigatórios)

| # | Arquivo |
|---|---------|
| 1 | `charts/01_tempo_total_pipeline.png` |
| 2 | `charts/02_tempo_por_job.png` |
| 3 | `charts/03_taxa_sucesso_falha.png` |
| 4 | `charts/04_testes_vs_duracao.png` |

Gerados por `scripts/generate_charts.py` a partir do CSV acima.

---

## 5. Pipeline (checklist)

- [x] Instalação de dependências
- [x] Lint (`ruff`)
- [x] Testes (`pytest` + JUnit)
- [x] Artefatos (`test-results-*`, `pipeline-metrics-*`)
- [x] Coleta de métricas no job `collect-metrics`
- [x] Script Python na API
- [x] 12+ execuções com variações
- [x] Relatório com análise → `docs/RELATORIO.md`

---

## 6. Como reproduzir

```bash
git clone https://github.com/RafaelBarbosa12/ponderada-metricas.git
cd ponderada-metricas
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# Disparar 12 variações
./scripts/push_variations.sh
./scripts/push_sequential_variations.sh

# Após as runs no GitHub
export GITHUB_TOKEN=$(gh auth token)
python scripts/collect_metrics.py --repo RafaelBarbosa12/ponderada-metricas --limit 40
python scripts/generate_charts.py
```

---

## 7. Texto para envio

> Ponderada CI/CD — métricas de pipeline.  
> Repo: https://github.com/RafaelBarbosa12/ponderada-metricas  
> Entregáveis: https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/entregaveis.md  
> Relatório: https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/docs/RELATORIO.md  
> Actions: https://github.com/RafaelBarbosa12/ponderada-metricas/actions  
