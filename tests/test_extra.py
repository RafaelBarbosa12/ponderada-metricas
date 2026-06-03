"""Testes extras — ativados quando EXPAND_TESTS=1 (variação do experimento)."""

import os

import pytest

from src.math_ops import add, multiply

pytestmark = pytest.mark.skipif(
    os.environ.get("EXPAND_TESTS", "0") != "1",
    reason="EXPAND_TESTS não definido",
)


def test_add_commutative():
    assert add(1, 2) == add(2, 1)


def test_multiply_zero():
    assert multiply(5, 0) == 0


def test_add_negative():
    assert add(-1, 1) == 0


def test_multiply_negative():
    assert multiply(-2, 3) == -6


def test_add_large():
    assert add(1000, 2000) == 3000
