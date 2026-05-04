from __future__ import annotations

import pandas as pd

from src.kpi_engine import calculate_kpis
from src.recommendation_engine import generate_recommendations


def test_recommendations_flag_low_profit_margin() -> None:
    df = pd.DataFrame(
        {
            "month": ["2025-01-01", "2025-02-01"],
            "region": ["Northeast", "Northeast"],
            "product_category": ["Product A", "Product A"],
            "customer_segment": ["Mid-Market", "Mid-Market"],
            "marketing_spend": [1000.0, 1000.0],
            "operating_cost": [7000.0, 7200.0],
            "units_sold": [100, 100],
            "average_price": [100.0, 100.0],
            "revenue": [10_000.0, 10_000.0],
            "gross_margin_rate": [0.4, 0.4],
            "gross_margin": [4_000.0, 4_000.0],
            "profit": [-4_000.0, -4_200.0],
            "retention_rate": [0.88, 0.88],
            "churn_risk": [0.12, 0.12],
        }
    )

    recommendations = generate_recommendations(df)

    assert recommendations[0]["priority"] == "High"
    assert any("cost" in rec["recommendation"].lower() for rec in recommendations)
    assert all("evidence" in rec and "action" in rec for rec in recommendations)


def test_recommendations_include_scenario_risk() -> None:
    df = pd.DataFrame(
        {
            "month": ["2025-01-01", "2025-02-01"],
            "region": ["Northeast", "West"],
            "product_category": ["Product A", "Product B"],
            "customer_segment": ["Enterprise", "Enterprise"],
            "marketing_spend": [500.0, 500.0],
            "operating_cost": [2000.0, 2000.0],
            "units_sold": [100, 100],
            "average_price": [150.0, 150.0],
            "revenue": [15_000.0, 15_000.0],
            "gross_margin_rate": [0.55, 0.55],
            "gross_margin": [8_250.0, 8_250.0],
            "profit": [5_750.0, 5_750.0],
            "retention_rate": [0.90, 0.90],
            "churn_risk": [0.10, 0.10],
        }
    )
    scenario = {"risk_level": "High", "profit_delta_pct": -15.0}

    recommendations = generate_recommendations(df, calculate_kpis(df), scenario)

    assert any(rec["theme"] == "Scenario risk" for rec in recommendations)


def test_recommendations_sort_high_priority_first() -> None:
    df = pd.DataFrame(
        {
            "month": ["2025-01-01", "2025-02-01"],
            "region": ["West", "West"],
            "product_category": ["Product A", "Product A"],
            "customer_segment": ["Small Business", "Small Business"],
            "marketing_spend": [1000.0, 1200.0],
            "operating_cost": [7000.0, 7600.0],
            "units_sold": [100, 100],
            "average_price": [100.0, 95.0],
            "revenue": [10_000.0, 9_500.0],
            "gross_margin_rate": [0.32, 0.31],
            "gross_margin": [3_200.0, 2_945.0],
            "profit": [-4_800.0, -5_855.0],
            "retention_rate": [0.75, 0.74],
            "churn_risk": [0.25, 0.26],
        }
    )

    recommendations = generate_recommendations(df)

    assert recommendations[0]["priority"] == "High"
    assert {rec["priority"] for rec in recommendations}.issuperset({"High"})
