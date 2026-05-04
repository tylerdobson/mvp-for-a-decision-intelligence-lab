"""Shared utility helpers for formatting, paths, and safe math."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide two numbers without raising on a zero denominator."""

    if denominator in (0, 0.0) or denominator is None:
        return default
    return numerator / denominator


def pct_change(current: float, previous: float) -> float:
    """Return percent change as percentage points, not a decimal."""

    if previous in (0, 0.0) or previous is None:
        return 0.0
    return ((current - previous) / abs(previous)) * 100


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Restrict a numeric value to a fixed range."""

    return max(minimum, min(maximum, value))


def format_currency(value: float) -> str:
    """Format a number as compact US dollars."""

    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{sign}${value / 1_000:.1f}K"
    return f"{sign}${value:,.0f}"


def format_number(value: float) -> str:
    """Format a numeric count for dashboard display."""

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def format_percentage(rate: float, decimals: int = 1) -> str:
    """Format a decimal rate as a percentage string."""

    return f"{rate * 100:.{decimals}f}%"


def format_delta_pct(value_pct: float, decimals: int = 1) -> str:
    """Format a percent-point delta with a sign."""

    return f"{value_pct:+.{decimals}f}%"
