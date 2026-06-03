#!/usr/bin/env python3
"""Grava métricas da execução atual do GitHub Actions em JSON (artefato do pipeline)."""

from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def parse_junit(path: Path) -> dict:
    if not path.exists():
        return {
            "test_count": 0,
            "test_failures": 0,
            "test_errors": 0,
            "test_skipped": 0,
            "test_time_avg_sec": 0.0,
        }
    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag == "testsuites":
        suites = root.findall("testsuite")
    else:
        suites = [root]
    total = failures = errors = skipped = 0
    times: list[float] = []
    for suite in suites:
        total += int(suite.attrib.get("tests", 0))
        failures += int(suite.attrib.get("failures", 0))
        errors += int(suite.attrib.get("errors", 0))
        skipped += int(suite.attrib.get("skipped", 0))
        for case in suite.findall("testcase"):
            t = case.attrib.get("time")
            if t:
                times.append(float(t))
    avg = sum(times) / len(times) if times else 0.0
    return {
        "test_count": total,
        "test_failures": failures + errors,
        "test_errors": errors,
        "test_skipped": skipped,
        "test_time_avg_sec": round(avg, 4),
    }


def main() -> int:
    out_dir = Path(os.environ.get("METRICS_DIR", "artifacts/metrics"))
    out_dir.mkdir(parents=True, exist_ok=True)

    junit = Path(os.environ.get("JUNIT_PATH", "reports/junit.xml"))
    test_stats = parse_junit(junit)

    variation = os.environ.get("EXPERIMENT_VARIATION", "default")
    parallel_mode = os.environ.get("PARALLEL_JOBS", "true").lower() == "true"
    cache_enabled = os.environ.get("CACHE_ENABLED", "true").lower() == "true"

    payload = {
        "run_id": int(os.environ.get("GITHUB_RUN_ID", 0)),
        "run_number": int(os.environ.get("GITHUB_RUN_NUMBER", 0)),
        "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "commit_sha": os.environ.get("GITHUB_SHA", ""),
        "commit_message": os.environ.get("COMMIT_MESSAGE", "")[:200],
        "ref": os.environ.get("GITHUB_REF", ""),
        "actor": os.environ.get("GITHUB_ACTOR", ""),
        "status": os.environ.get("JOB_STATUS", "unknown"),
        "conclusion": os.environ.get("JOB_CONCLUSION", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "experiment_variation": variation,
        "parallel_jobs": parallel_mode,
        "cache_enabled": cache_enabled,
        "expand_tests": os.environ.get("EXPAND_TESTS", "0") == "1",
        "run_slow_tests": os.environ.get("RUN_SLOW_TESTS", "0") == "1",
        "intentional_fail": os.environ.get("INTENTIONAL_FAIL", "0") == "1",
        **test_stats,
    }

    # Timings opcionais passados pelo workflow
    for key in (
        "workflow_duration_sec",
        "job_lint_duration_sec",
        "job_test_duration_sec",
        "job_metrics_duration_sec",
        "step_install_duration_sec",
        "step_lint_duration_sec",
        "step_test_duration_sec",
    ):
        env_key = key.upper()
        if os.environ.get(env_key):
            payload[key] = float(os.environ[env_key])

    out_file = out_dir / f"run_{payload['run_id']}.json"
    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Métricas gravadas em {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
