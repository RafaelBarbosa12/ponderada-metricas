#!/usr/bin/env python3
"""Lê experiment-config.json e exporta variáveis para o GITHUB_ENV."""

import json
import os
from pathlib import Path

CONFIG = Path("experiment-config.json")
EVENT = os.environ.get("GITHUB_EVENT_NAME", "")

defaults = {
    "EXPERIMENT_VARIATION": os.environ.get("EXPERIMENT_VARIATION", "push-default"),
    "PARALLEL_JOBS": os.environ.get("PARALLEL_JOBS", "true"),
    "CACHE_ENABLED": os.environ.get("CACHE_ENABLED", "true"),
    "EXPAND_TESTS": os.environ.get("EXPAND_TESTS", "0"),
    "RUN_SLOW_TESTS": os.environ.get("RUN_SLOW_TESTS", "0"),
    "INTENTIONAL_FAIL": os.environ.get("INTENTIONAL_FAIL", "0"),
}

if EVENT == "push" and CONFIG.exists():
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    defaults["EXPERIMENT_VARIATION"] = data.get("experiment_variation", "push-default")
    defaults["PARALLEL_JOBS"] = "true" if data.get("parallel_jobs", True) else "false"
    defaults["CACHE_ENABLED"] = "true" if data.get("cache_enabled", True) else "false"
    defaults["EXPAND_TESTS"] = "1" if data.get("expand_tests") else "0"
    defaults["RUN_SLOW_TESTS"] = "1" if data.get("run_slow_tests") else "0"
    defaults["INTENTIONAL_FAIL"] = "1" if data.get("intentional_fail") else "0"

with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as env_file:
    for key, value in defaults.items():
        env_file.write(f"{key}={value}\n")

print("Config ativa:", defaults)
