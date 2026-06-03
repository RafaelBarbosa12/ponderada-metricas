#!/usr/bin/env python3
"""
Coleta métricas reais do GitHub Actions via API e gera CSV/JSON.

Uso:
  export GITHUB_TOKEN=ghp_...
  python scripts/collect_metrics.py --repo RafaelBarbosa12/ponderada-hermano

Requer permissões: actions:read, contents:read (para commits).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import requests

API = "https://api.github.com"
WORKFLOW_NAME = "CI/CD Métricas"
CSV_FIELDS = [
    "run_id",
    "run_number",
    "commit_sha",
    "commit_message",
    "status",
    "conclusion",
    "workflow_duration_sec",
    "job_name",
    "job_duration_sec",
    "step_name",
    "step_duration_sec",
    "test_count",
    "test_failures",
    "test_time_avg_sec",
    "timestamp",
    "experiment_variation",
    "parallel_jobs",
    "cache_enabled",
    "expand_tests",
    "run_slow_tests",
    "intentional_fail",
    "html_url",
]


def headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def duration_sec(start: str | None, end: str | None) -> float:
    s, e = parse_iso(start), parse_iso(end)
    if not s or not e:
        return 0.0
    return max(0.0, (e - s).total_seconds())


def get_workflow_id(session: requests.Session, repo: str) -> int:
    r = session.get(f"{API}/repos/{repo}/actions/workflows", timeout=60)
    r.raise_for_status()
    for wf in r.json().get("workflows", []):
        if wf.get("name") == WORKFLOW_NAME or wf.get("path", "").endswith("ci.yml"):
            return wf["id"]
    raise RuntimeError(f"Workflow '{WORKFLOW_NAME}' não encontrado em {repo}")


def list_runs(session: requests.Session, repo: str, workflow_id: int, limit: int) -> list:
    r = session.get(
        f"{API}/repos/{repo}/actions/workflows/{workflow_id}/runs",
        params={"per_page": min(limit, 100)},
        timeout=60,
    )
    r.raise_for_status()
    return r.json().get("workflow_runs", [])[:limit]


def get_jobs(session: requests.Session, repo: str, run_id: int) -> list:
    r = session.get(f"{API}/repos/{repo}/actions/runs/{run_id}/jobs", timeout=60)
    r.raise_for_status()
    return r.json().get("jobs", [])


def get_commit_message(session: requests.Session, repo: str, sha: str) -> str:
    r = session.get(f"{API}/repos/{repo}/commits/{sha}", timeout=60)
    if r.status_code != 200:
        return ""
    msg = r.json().get("commit", {}).get("message", "")
    return (msg.split("\n")[0] if msg else "")[:200]


def download_artifact_metrics(
    session: requests.Session, repo: str, run_id: int
) -> dict | None:
    """Tenta baixar JSON de métricas gerado pelo pipeline."""
    r = session.get(f"{API}/repos/{repo}/actions/runs/{run_id}/artifacts", timeout=60)
    if r.status_code != 200:
        return None
    artifacts = r.json().get("artifacts", [])
    target = None
    for art in artifacts:
        if art.get("name", "").startswith("pipeline-metrics-"):
            target = art
            break
    if not target:
        return None
    r2 = session.get(
        f"{API}/repos/{repo}/actions/artifacts/{target['id']}/zip",
        timeout=120,
        allow_redirects=True,
    )
    if r2.status_code != 200:
        return None
    try:
        with zipfile.ZipFile(BytesIO(r2.content)) as zf:
            for name in zf.namelist():
                if name.endswith(".json") and "run_" in name:
                    return json.loads(zf.read(name).decode("utf-8"))
    except (zipfile.BadZipFile, json.JSONDecodeError):
        return None
    return None


def parse_junit_bytes(data: bytes) -> dict:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return {"test_count": 0, "test_failures": 0, "test_time_avg_sec": 0.0}
    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
    total = failures = 0
    times: list[float] = []
    for suite in suites:
        total += int(suite.attrib.get("tests", 0))
        failures += int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
        for case in suite.findall("testcase"):
            if case.attrib.get("time"):
                times.append(float(case.attrib["time"]))
    return {
        "test_count": total,
        "test_failures": failures,
        "test_time_avg_sec": round(sum(times) / len(times), 4) if times else 0.0,
    }


def download_junit_from_test_artifact(session: requests.Session, repo: str, run_id: int) -> dict:
    r = session.get(f"{API}/repos/{repo}/actions/runs/{run_id}/artifacts", timeout=60)
    if r.status_code != 200:
        return {"test_count": 0, "test_failures": 0, "test_time_avg_sec": 0.0}
    for art in r.json().get("artifacts", []):
        if not art.get("name", "").startswith("test-results-"):
            continue
        r2 = session.get(
            f"{API}/repos/{repo}/actions/artifacts/{art['id']}/zip",
            timeout=120,
            allow_redirects=True,
        )
        if r2.status_code != 200:
            continue
        try:
            with zipfile.ZipFile(BytesIO(r2.content)) as zf:
                for name in zf.namelist():
                    if name.endswith("junit.xml"):
                        return parse_junit_bytes(zf.read(name))
        except zipfile.BadZipFile:
            continue
    return {"test_count": 0, "test_failures": 0, "test_time_avg_sec": 0.0}


def infer_variation(message: str, artifact: dict | None) -> str:
    if artifact and artifact.get("experiment_variation"):
        return artifact["experiment_variation"]
    if message.startswith("exp:"):
        return message.split(":", 1)[1].strip()[:80]
    return "unknown"


def collect(repo: str, token: str, limit: int, out_dir: Path) -> Path:
    session = requests.Session()
    session.headers.update(headers(token))

    workflow_id = get_workflow_id(session, repo)
    runs = list_runs(session, repo, workflow_id, limit)
    rows: list[dict] = []

    for run in runs:
        run_id = run["id"]
        sha = run.get("head_sha", "")
        message = get_commit_message(session, repo, sha)
        artifact = download_artifact_metrics(session, repo, run_id)
        junit = download_junit_from_test_artifact(session, repo, run_id)

        test_count = junit["test_count"]
        test_failures = junit["test_failures"]
        test_avg = junit["test_time_avg_sec"]
        if artifact:
            test_count = artifact.get("test_count", test_count)
            test_failures = artifact.get("test_failures", test_failures)
            test_avg = artifact.get("test_time_avg_sec", test_avg)

        wf_duration = duration_sec(run.get("run_started_at"), run.get("updated_at"))
        variation = infer_variation(message, artifact)
        parallel = artifact.get("parallel_jobs", True) if artifact else True
        cache = artifact.get("cache_enabled", True) if artifact else True

        jobs = get_jobs(session, repo, run_id)
        if not jobs:
            rows.append(
                {
                    "run_id": run_id,
                    "run_number": run.get("run_number"),
                    "commit_sha": sha,
                    "commit_message": message,
                    "status": run.get("status"),
                    "conclusion": run.get("conclusion"),
                    "workflow_duration_sec": round(wf_duration, 2),
                    "job_name": "_workflow",
                    "job_duration_sec": round(wf_duration, 2),
                    "step_name": "",
                    "step_duration_sec": 0,
                    "test_count": test_count,
                    "test_failures": test_failures,
                    "test_time_avg_sec": test_avg,
                    "timestamp": run.get("run_started_at", ""),
                    "experiment_variation": variation,
                    "parallel_jobs": parallel,
                    "cache_enabled": cache,
                    "expand_tests": artifact.get("expand_tests", False) if artifact else False,
                    "run_slow_tests": artifact.get("run_slow_tests", False) if artifact else False,
                    "intentional_fail": artifact.get("intentional_fail", False) if artifact else False,
                    "html_url": run.get("html_url", ""),
                }
            )
            continue

        for job in jobs:
            job_dur = duration_sec(job.get("started_at"), job.get("completed_at"))
            steps = job.get("steps") or []
            if steps:
                for step in steps:
                    step_dur = duration_sec(step.get("started_at"), step.get("completed_at"))
                    rows.append(
                        {
                            "run_id": run_id,
                            "run_number": run.get("run_number"),
                            "commit_sha": sha,
                            "commit_message": message,
                            "status": run.get("status"),
                            "conclusion": run.get("conclusion"),
                            "workflow_duration_sec": round(wf_duration, 2),
                            "job_name": job.get("name", ""),
                            "job_duration_sec": round(job_dur, 2),
                            "step_name": step.get("name", ""),
                            "step_duration_sec": round(step_dur, 2),
                            "test_count": test_count,
                            "test_failures": test_failures,
                            "test_time_avg_sec": test_avg,
                            "timestamp": run.get("run_started_at", ""),
                            "experiment_variation": variation,
                            "parallel_jobs": parallel,
                            "cache_enabled": cache,
                            "expand_tests": artifact.get("expand_tests", False) if artifact else False,
                            "run_slow_tests": artifact.get("run_slow_tests", False) if artifact else False,
                            "intentional_fail": artifact.get("intentional_fail", False)
                            if artifact
                            else False,
                            "html_url": run.get("html_url", ""),
                        }
                    )
            else:
                rows.append(
                    {
                        "run_id": run_id,
                        "run_number": run.get("run_number"),
                        "commit_sha": sha,
                        "commit_message": message,
                        "status": run.get("status"),
                        "conclusion": run.get("conclusion"),
                        "workflow_duration_sec": round(wf_duration, 2),
                        "job_name": job.get("name", ""),
                        "job_duration_sec": round(job_dur, 2),
                        "step_name": "",
                        "step_duration_sec": 0,
                        "test_count": test_count,
                        "test_failures": test_failures,
                        "test_time_avg_sec": test_avg,
                        "timestamp": run.get("run_started_at", ""),
                        "experiment_variation": variation,
                        "parallel_jobs": parallel,
                        "cache_enabled": cache,
                        "expand_tests": False,
                        "run_slow_tests": False,
                        "intentional_fail": False,
                        "html_url": run.get("html_url", ""),
                    }
                )
        time.sleep(0.3)

    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"metrics_{ts}.csv"
    json_path = out_dir / f"metrics_{ts}.json"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    latest = out_dir / "metrics_latest.csv"
    latest.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")
    (out_dir / "metrics_latest.json").write_text(
        json_path.read_text(encoding="utf-8"), encoding="utf-8"
    )

    print(f"Coletadas {len(runs)} execuções → {len(rows)} linhas")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    return csv_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta métricas do GitHub Actions")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "RafaelBarbosa12/ponderada-hermano"))
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--out", type=Path, default=Path("data/metrics"))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    args = parser.parse_args()

    if not args.token:
        print(
            "Erro: defina GITHUB_TOKEN ou GH_TOKEN com permissão actions:read.",
            file=sys.stderr,
        )
        return 1

    try:
        collect(args.repo, args.token, args.limit, args.out)
    except requests.HTTPError as e:
        print(f"Erro API: {e.response.status_code} {e.response.text[:300]}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
