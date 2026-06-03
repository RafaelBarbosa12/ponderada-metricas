# Experimento CI/CD — Métricas de Pipeline

Repositório da atividade de instrumentação e análise de pipeline GitHub Actions.

**Repositório:** https://github.com/RafaelBarbosa12/ponderada-metricas  
**Entregáveis (índice):** [entregaveis/ENTREGAVEIS.md](entregaveis/ENTREGAVEIS.md)  
**Workflow:** [.github/workflows/ci.yml](.github/workflows/ci.yml)

## Estrutura

| Caminho | Descrição |
|---------|-----------|
| `src/`, `tests/` | Projeto Python de exemplo com testes pytest |
| `.github/workflows/ci.yml` | Pipeline: deps, lint (ruff), testes, artefatos, métricas |
| `scripts/collect_metrics.py` | Coleta métricas reais via API do GitHub |
| `scripts/generate_charts.py` | Gera 4 gráficos obrigatórios |
| `scripts/trigger_experiments.sh` | Dispara 12 variações via `workflow_dispatch` |
| `data/metrics/` | CSV/JSON gerados pelo script de coleta |
| `charts/` | PNG dos gráficos |
| `docs/RELATORIO.md` | Relatório técnico da atividade |
| `entregaveis/ENTREGAVEIS.md` | Índice com links e dados de entrega |

## Reproduzir o experimento

### 1. Pré-requisitos

- Python 3.11+
- [GitHub CLI](https://cli.github.com/) (`gh auth login`)
- Token com `actions:read` (o `gh auth token` já serve)

### 2. Subir o código (se ainda não estiver no GitHub)

```bash
git add .
git commit -m "feat: projeto base CI/CD métricas"
git push -u origin main
```

### 3. Executar 12+ pipelines

```bash
chmod +x scripts/trigger_experiments.sh
./scripts/trigger_experiments.sh RafaelBarbosa12/ponderada-metricas
```

Aguarde todas as runs em: https://github.com/RafaelBarbosa12/ponderada-metricas/actions

### 4. Coletar métricas e gerar gráficos

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

export GITHUB_TOKEN=$(gh auth token)
python scripts/collect_metrics.py --repo RafaelBarbosa12/ponderada-metricas --limit 30
python scripts/generate_charts.py
```

### 5. Relatório

Atualize `docs/RELATORIO.md` com os run IDs e commits reais listados pelo script de coleta.

## Métricas coletadas

- Tempo total do workflow e por job/etapa (API GitHub)
- Status e conclusão (success/failure)
- Quantidade de testes e falhas (JUnit nos artefatos)
- Tempo médio dos testes, SHA, mensagem e timestamp do commit
- Metadados de variação (cache, paralelismo, flags do experimento)

## Desenvolvimento local

```bash
pip install -r requirements-dev.txt
ruff check src tests
pytest
```
