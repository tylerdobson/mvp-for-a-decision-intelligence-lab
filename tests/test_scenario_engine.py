from __future__ import annotations

from src.scenario_engine import run_scenario


BASELINE = {
    "revenue": 100_000.0,
    "profit": 12_000.0,
    "gross_margin": 45_000.0,
    "operating_cost": 25_000.0,
    "marketing_spend": 8_000.0,
    "units_sold": 1_000.0,
    "average_price": 100.0,
}


def test_scenario_positive_demand_increases_revenue() -> None:
    result = run_scenario(BASELINE, demand_change_pct=10)

    assert result["adjusted_revenue"] > BASELINE["revenue"]
    assert result["revenue_delta_pct"] > 0


def test_scenario_price_increase_can_reduce_demand() -> None:
    result = run_scenario(BASELINE, price_change_pct=10)

    assert round(float(result["demand_multiplier"]), 3) == 0.965
    assert result["adjusted_revenue"] > 0


def test_scenario_high_cost_pressure_is_risky() -> None:
    result = run_scenario(BASELINE, cost_change_pct=40)

    assert result["risk_level"] == "High"
    assert "Revise" in result["recommended_action"] or "Do not" in result["recommended_action"]


def test_scenario_retention_change_updates_retention_and_churn() -> None:
    baseline = {**BASELINE, "retention_rate": 0.80}

    result = run_scenario(baseline, retention_change_pct=10)

    assert round(float(result["adjusted_retention_rate"]), 3) == 0.88
    assert round(float(result["adjusted_churn_risk"]), 3) == 0.12
    assert result["demand_multiplier"] > 1
