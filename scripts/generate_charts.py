#!/usr/bin/env python3
"""Gera os 4+ gráficos obrigatórios a partir do CSV de métricas."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_data(csv_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("CSV vazio — execute collect_metrics.py após as runs no GitHub")

    runs = (
        df.groupby("run_id", as_index=False)
        .agg(
            {
                "workflow_duration_sec": "first",
                "conclusion": "first",
                "commit_message": "first",
                "experiment_variation": "first",
                "test_count": "first",
                "test_failures": "first",
                "timestamp": "first",
                "run_number": "first",
            }
        )
        .sort_values("run_number")
    )
    jobs = df[df["step_name"] == ""].drop_duplicates(subset=["run_id", "job_name"])
    if jobs.empty:
        jobs = df.groupby(["run_id", "job_name"], as_index=False)["job_duration_sec"].max()
    return runs, jobs


def chart_pipeline_duration(runs: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = runs["run_number"].astype(str)
    ax.bar(labels, runs["workflow_duration_sec"], color="#2563eb")
    ax.set_xlabel("Número da execução (run_number)")
    ax.set_ylabel("Duração total (s)")
    ax.set_title("Tempo total do pipeline por execução")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def chart_job_duration(jobs: pd.DataFrame, out: Path) -> None:
    pivot = jobs.pivot_table(
        index="run_id", columns="job_name", values="job_duration_sec", aggfunc="max"
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    pivot.plot(kind="bar", ax=ax, width=0.8)
    ax.set_xlabel("run_id")
    ax.set_ylabel("Duração do job (s)")
    ax.set_title("Tempo por job em cada execução")
    ax.legend(title="Job", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_success_rate(runs: pd.DataFrame, out: Path) -> None:
    runs = runs.copy()
    runs["ok"] = runs["conclusion"] == "success"
    rate = runs["ok"].mean() * 100
    counts = runs["conclusion"].value_counts()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].pie(
        counts.values,
        labels=counts.index,
        autopct="%1.0f%%",
        colors=["#22c55e", "#ef4444", "#f59e0b"][: len(counts)],
    )
    axes[0].set_title("Distribuição sucesso / falha")
    axes[1].bar(["Taxa de sucesso"], [rate], color="#22c55e" if rate >= 50 else "#ef4444")
    axes[1].set_ylim(0, 100)
    axes[1].set_ylabel("%")
    axes[1].set_title(f"Taxa de sucesso agregada: {rate:.1f}%")
    plt.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def chart_tests_vs_duration(runs: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    sc = ax.scatter(
        runs["test_count"],
        runs["workflow_duration_sec"],
        c=runs["test_failures"],
        cmap="coolwarm",
        s=80,
        edgecolors="black",
        linewidths=0.5,
    )
    for _, row in runs.iterrows():
        ax.annotate(
            str(int(row["run_number"])),
            (row["test_count"], row["workflow_duration_sec"]),
            fontsize=8,
            ha="center",
        )
    plt.colorbar(sc, label="Falhas de teste")
    ax.set_xlabel("Quantidade de testes")
    ax.set_ylabel("Duração do workflow (s)")
    ax.set_title("Testes vs duração do pipeline")
    plt.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data/metrics/metrics_latest.csv"),
    )
    parser.add_argument("--out", type=Path, default=Path("charts"))
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"Arquivo não encontrado: {args.csv}", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    runs, jobs = load_data(args.csv)

    chart_pipeline_duration(runs, args.out / "01_tempo_total_pipeline.png")
    chart_job_duration(jobs, args.out / "02_tempo_por_job.png")
    chart_success_rate(runs, args.out / "03_taxa_sucesso_falha.png")
    chart_tests_vs_duration(runs, args.out / "04_testes_vs_duracao.png")

    print("Gráficos gerados em", args.out)
    for p in sorted(args.out.glob("0*.png")):
        print(" ", p.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
