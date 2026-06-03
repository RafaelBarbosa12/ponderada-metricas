# Por que você recebeu e-mails de falha do GitHub?

## 1. Falhas **de propósito** (parte da atividade)

Os commits `exp:07-falha-intencional` e `exp:11-sequencial-falha` ativam um teste que **deve falhar** para medir métricas de pipeline com erro. Isso gera e-mail do GitHub — é esperado no experimento, não é bug do projeto.

As falhas aparecem no JUnit; o workflow foi ajustado para não quebrar o job de métricas.

## 2. Bug: dois workflows ao mesmo tempo

O workflow **sequencial** estava configurado para rodar em **todo** commit que alterava `experiment-config.json`, além do workflow principal. Resultado:

- 2 pipelines por commit
- O sequencial **não lia** o `experiment-config.json` → comportamento errado
- Mais e-mails de falha

**Correção:** o sequencial só roda quando o arquivo `.sequential-marker` é alterado no commit.

## 3. O que fazer agora

1. O fix já está no repositório — o próximo push em `main` deve ficar **verde** (sem `intentional_fail`).
2. Para repetir o experimento de falha: use **Actions → Run workflow** e marque `intentional_fail`, ou faça um commit com `"intentional_fail": true` no JSON **sabendo** que o GitHub pode enviar e-mail.
3. Para silenciar e-mails: GitHub → **Settings → Notifications** → desmarque falhas de Actions (opcional).

## 4. Variáveis do experimento

Tudo passa por `experiment-config.json` + `scripts/load_experiment_config.py` no início de cada job. Não é preciso copiar flags manualmente no YAML.
