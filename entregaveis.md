# Entregáveis — Ponderada CI/CD (métricas de pipeline)

**Aluno:** Rafael Barbosa  
**Repositório de entrega:** https://github.com/RafaelBarbosa12/ponderada-metricas  

*Uso de IA para ajudar na documentacao e organizacao de pastas e textos*

---

## 1. Links obrigatórios (copiar para o professor)

| Item | Link |
|------|------|
| Repositório GitHub | https://github.com/RafaelBarbosa12/ponderada-metricas |
| Workflow principal (YAML) | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/.github/workflows/ci.yml |
| Workflow sequencial (YAML) | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/.github/workflows/ci-sequential.yml |
| GitHub Actions (execuções) | https://github.com/RafaelBarbosa12/ponderada-metricas/actions |
| Script de coleta (Python) | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/scripts/collect_metrics.py |
| Script de gráficos | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/scripts/generate_charts.py |
| Base CSV | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/data/metrics/metrics_latest.csv |
| Base JSON | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/data/metrics/metrics_latest.json |
| Relatório técnico | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/docs/RELATORIO.md |
| Este índice de entrega | https://github.com/RafaelBarbosa12/ponderada-metricas/blob/main/entregaveis.md |

---

## 2. Run de referência no repositório atual (`ponderada-metricas`)

Primeira execução bem-sucedida após migração do código corrigido.

| Campo | Valor |
|-------|--------|
| **run_id** | `26889954640` |
| **run_number** | `1` |
| **URL** | https://github.com/RafaelBarbosa12/ponderada-metricas/actions/runs/26889954640 |
| **workflow** | CI/CD Métricas |
| **conclusion** | `success` |
| **commit_sha** | `e8b43b9540267f868461c19987f93ecf46fa307d` |
| **commit_message** | docs: entrega final da ponderada — métricas, gráficos e relatório |
| **experiment_variation** | `push-default` |
| **parallel_jobs** | `true` |
| **cache_enabled** | `true` |
| **test_count** | `13` |
| **test_failures** | `0` |
| **test_skipped** | `7` |
| **test_time_avg_sec** | `0.0001` |

### JSON gerado pelo job `collect-metrics` (run 26889954640)

```json
{
  "run_id": 26889954640,
  "run_number": 1,
  "workflow": "CI/CD Métricas",
  "repository": "RafaelBarbosa12/ponderada-metricas",
  "commit_sha": "e8b43b9540267f868461c19987f93ecf46fa307d",
  "commit_message": "docs: entrega final da ponderada — métricas, gráficos e relatório",
  "ref": "refs/heads/main",
  "actor": "RafaelBarbosa12",
  "status": "success",
  "conclusion": "success",
  "timestamp": "2026-06-03T14:06:54.410242+00:00",
  "experiment_variation": "push-default",
  "parallel_jobs": true,
  "cache_enabled": true,
  "expand_tests": false,
  "run_slow_tests": false,
  "intentional_fail": false,
  "test_count": 13,
  "test_failures": 0,
  "test_errors": 0,
  "test_skipped": 7,
  "test_time_avg_sec": 0.0001,
  "needs_test": "success",
  "needs_lint": "success"
}
```

---

## 3. Arquivos no repositório (caminhos locais)

| Entregável | Caminho |
|------------|---------|
| Projeto + testes | `src/`, `tests/` |
| Pipeline paralelo | `.github/workflows/ci.yml` |
| Pipeline sequencial | `.github/workflows/ci-sequential.yml` |
| Config de variações | `experiment-config.json` |
| Métricas no pipeline | `scripts/record_pipeline_metrics.py` |
| Coleta via API | `scripts/collect_metrics.py` |
| Gráficos | `scripts/generate_charts.py` → `charts/*.png` |
| Dados tabulares | `data/metrics/metrics_latest.csv`, `metrics_latest.json` |
| Relatório completo | `docs/RELATORIO.md` |
| Variações planejadas | `experiments/VARIATIONS.md` |
| Como reproduzir | `README.md` |

### Gráficos (4 obrigatórios)

| # | Arquivo |
|---|---------|
| 1 | `charts/01_tempo_total_pipeline.png` |
| 2 | `charts/02_tempo_por_job.png` |
| 3 | `charts/03_taxa_sucesso_falha.png` |
| 4 | `charts/04_testes_vs_duracao.png` |

---

## 4. O que o pipeline faz (checklist da atividade)

- [x] Instalação de dependências (`pip install -r requirements-dev.txt`)
- [x] Lint / análise estática (`ruff check`)
- [x] Testes automatizados (`pytest` + JUnit XML)
- [x] Artefato com resultados (`test-results-{run_id}`)
- [x] Coleta de métricas no job `collect-metrics` + artefato `pipeline-metrics-{run_id}`
- [x] Script Python próprio consultando API (`collect_metrics.py`)
- [x] CSV/JSON estruturado
- [x] Quatro gráficos
- [x] Relatório técnico em Markdown

---

## 5. Experimento com 12+ variações

O planejamento das 12 variações está em `experiments/VARIATIONS.md`.

**Histórico completo (22 runs, 12+ variações):** coletado no repositório anterior `ponderada-hermano` — dados em `data/metrics/metrics_latest.csv` e análise em `docs/RELATORIO.md`.

**Repositório atual (`ponderada-metricas`):** código final + run **#1** (`26889954640`). Para repetir as 12 variações só neste repo:

```bash
./scripts/push_variations.sh RafaelBarbosa12/ponderada-metricas
./scripts/push_sequential_variations.sh RafaelBarbosa12/ponderada-metricas
export GITHUB_TOKEN=$(gh auth token)
python scripts/collect_metrics.py --repo RafaelBarbosa12/ponderada-metricas --limit 30
python scripts/generate_charts.py
```

---

## 6. Como reproduzir (resumo)

```bash
git clone https://github.com/RafaelBarbosa12/ponderada-metricas.git
cd ponderada-metricas
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

ruff check src tests
pytest

export GITHUB_TOKEN=$(gh auth token)
python scripts/collect_metrics.py --repo RafaelBarbosa12/ponderada-metricas
python scripts/generate_charts.py
```

---

## 7. Relatório

Respostas detalhadas: **[docs/RELATORIO.md](docs/RELATORIO.md)**

---