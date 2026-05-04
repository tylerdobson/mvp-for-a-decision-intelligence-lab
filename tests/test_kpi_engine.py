from __future__ import annotations

import pandas as pd

from src.kpi_engine import calculate_kpis, monthly_trends, performance_by_dimension


def test_calculate_kpis_totals_and_margin() -> None:
    df = pd.DataFrame(
        {
            "month": ["2025-01-01", "2025-02-01"],
            "region": ["Northeast", "Northeast"],
            "product_category": ["Software", "Software"],
            "customer_segment": ["Mid-Market", "Mid-Market"],
            "marketing_spend": [100.0, 120.0],
            "operating_cost": [300.0, 330.0],
            "units_sold": [10, 12],
            "average_price": [100.0, 100.0],
            "revenue": [1_000.0, 1_200.0],
            "gross_margin_rate": [0.5, 0.5],
            "gross_margin": [500.0, 600.0],
            "profit": [100.0, 150.0],
            "retention_rate": [0.85, 0.87],
            "churn_risk": [0.15, 0.13],
        }
    )

    kpis = calculate_kpis(df)

    assert kpis["revenue"] == 2_200.0
    assert kpis["profit"] == 250.0
    assert round(float(kpis["gross_margin_rate"]), 4) == 0.5
    assert round(float(kpis["revenue_mom_pct"]), 2) == 20.0
    assert round(float(kpis["profit_mom_pct"]), 2) == 50.0


def test_monthly_trends_returns_expected_columns() -> None:
    df = pd.DataFrame(
        {
            "month": ["2025-01-01", "2025-01-01"],
            "region": ["Northeast", "South"],
            "product_category": ["Software", "Support"],
            "customer_segment": ["Mid-Market", "Enterprise"],
            "marketing_spend": [100.0, 200.0],
            "operating_cost": [300.0, 400.0],
            "units_sold": [10, 20],
            "average_price": [100.0, 120.0],
            "revenue": [1_000.0, 2_400.0],
            "gross_margin_rate": [0.5, 0.4],
            "gross_margin": [500.0, 960.0],
            "profit": [100.0, 360.0],
            "retention_rate": [0.85, 0.90],
            "churn_risk": [0.15, 0.10],
        }
    )

    trends = monthly_trends(df)

    assert len(trends) == 1
    assert trends.loc[0, "revenue"] == 3_400.0
    assert round(trends.loc[0, "profit_margin"], 4) == round(460 / 3400, 4)


def test_performance_by_dimension_orders_by_profit() -> None:
    df = pd.DataFrame(
        {
            "month": ["2025-01-01", "2025-01-01"],
            "region": ["Northeast", "South"],
            "product_category": ["Software", "Support"],
            "customer_segment": ["Mid-Market", "Enterprise"],
            "marketing_spend": [100.0, 100.0],
            "operating_cost": [250.0, 250.0],
            "units_sold": [10, 10],
            "average_price": [100.0, 100.0],
            "revenue": [1_000.0, 1_000.0],
            "gross_margin_rate": [0.5, 0.3],
            "gross_margin": [500.0, 300.0],
            "profit": [150.0, -50.0],
            "retention_rate": [0.85, 0.75],
            "churn_risk": [0.15, 0.25],
        }
    )

    perf = performance_by_dimension(df, "region")

    assert perf.loc[0, "region"] == "Northeast"
    assert perf.loc[1, "region"] == "South"
