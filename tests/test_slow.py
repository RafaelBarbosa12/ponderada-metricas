"""Teste lento — ativado com RUN_SLOW_TESTS=1."""

import os
import time

import pytest

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(
        os.environ.get("RUN_SLOW_TESTS", "0") != "1",
        reason="RUN_SLOW_TESTS não definido",
    ),
]


def test_slow_computation():
    time.sleep(3)
