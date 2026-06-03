"""Teste que falha — ativado com INTENTIONAL_FAIL=1."""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("INTENTIONAL_FAIL", "0") != "1",
    reason="INTENTIONAL_FAIL não definido",
)


def test_should_fail():
    assert 1 == 2, "falha intencional para métricas de pipeline"
