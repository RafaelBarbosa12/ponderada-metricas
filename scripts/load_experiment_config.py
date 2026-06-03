#!/usr/bin/env python3
"""Lê experiment-config.json e exporta variáveis para o GITHUB_ENV."""

import json
import os
from pathlib import Path

CONFIG = Path("experiment-config.json")
EVENT = os.environ.get("GITHUB_EVENT_NAME", "")
EVENT_PATH = Path(os.environ.get("GITHUB_EVENT_PATH", ""))


def _dispatch_inputs() -> dict:
    if not EVENT_PATH.is_file():
        return {}
    event = json.loads(EVENT_PATH.read_text(encoding="utf-8"))
    inp = event.get("inputs") or {}
    if not inp:
        return {}
    out: dict = {}
    if inp.get("experiment_variation"):
        out["EXPERIMENT_VARIATION"] = inp["experiment_variation"]
    for key, env_key in (
        ("cache_enabled", "CACHE_ENABLED"),
        ("expand_tests", "EXPAND_TESTS"),
        ("run_slow_tests", "RUN_SLOW_TESTS"),
        ("intentional_fail", "INTENTIONAL_FAIL"),
        ("parallel_jobs", "PARALLEL_JOBS"),
    ):
        if key not in inp:
            continue
        val = inp[key]
        if env_key in ("EXPAND_TESTS", "RUN_SLOW_TESTS", "INTENTIONAL_FAIL"):
            out[env_key] = "1" if str(val).lower() == "true" else "0"
        elif env_key == "PARALLEL_JOBS":
            out[env_key] = "true" if str(val).lower() == "true" else "false"
        else:
            out[env_key] = "true" if str(val).lower() == "true" else "false"
    return out


defaults = {
    "EXPERIMENT_VARIATION": os.environ.get("EXPERIMENT_VARIATION", "push-default"),
    "PARALLEL_JOBS": os.environ.get("PARALLEL_JOBS", "true"),
    "CACHE_ENABLED": os.environ.get("CACHE_ENABLED", "true"),
    "EXPAND_TESTS": os.environ.get("EXPAND_TESTS", "0"),
    "RUN_SLOW_TESTS": os.environ.get("RUN_SLOW_TESTS", "0"),
    "INTENTIONAL_FAIL": os.environ.get("INTENTIONAL_FAIL", "0"),
}

# Push e workflow_dispatch: prioriza experiment-config.json quando existir
if CONFIG.exists() and (EVENT == "push" or EVENT == "workflow_dispatch"):
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    defaults["EXPERIMENT_VARIATION"] = data.get("experiment_variation", "push-default")
    defaults["PARALLEL_JOBS"] = "true" if data.get("parallel_jobs", True) else "false"
    defaults["CACHE_ENABLED"] = "true" if data.get("cache_enabled", True) else "false"
    defaults["EXPAND_TESTS"] = "1" if data.get("expand_tests") else "0"
    defaults["RUN_SLOW_TESTS"] = "1" if data.get("run_slow_tests") else "0"
    defaults["INTENTIONAL_FAIL"] = "1" if data.get("intentional_fail") else "0"

if EVENT == "workflow_dispatch":
    defaults.update(_dispatch_inputs())

with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as env_file:
    for key, value in defaults.items():
        env_file.write(f"{key}={value}\n")

print("Config ativa:", defaults)
