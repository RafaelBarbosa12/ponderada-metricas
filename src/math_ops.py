"""Operações matemáticas simples para o experimento de CI/CD."""


def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("divisão por zero")
    return a / b


def power(base: float, exp: float) -> float:
    return base**exp
