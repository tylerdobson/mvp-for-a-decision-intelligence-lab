from __future__ import annotations

import pandas as pd

from src.forecasting import forecast_revenue, forecast_summary


def test_forecast_revenue_returns_history_and_requested_periods() -> None:
    df = pd.DataFrame(
        {
            "month": ["2025-01-01", "2025-02-01", "2025-03-01"],
            "region": ["Northeast"] * 3,
            "product_category": ["Software"] * 3,
            "customer_segment": ["Mid-Market"] * 3,
            "marketing_spend": [100.0, 120.0, 130.0],
            "operating_cost": [300.0, 310.0, 320.0],
            "units_sold": [10, 11, 12],
            "average_price": [100.0, 100.0, 100.0],
            "revenue": [1_000.0, 1_100.0, 1_200.0],
            "gross_margin_rate": [0.5, 0.5, 0.5],
            "gross_margin": [500.0, 550.0, 600.0],
            "profit": [100.0, 120.0, 140.0],
            "retention_rate": [0.85, 0.85, 0.85],
            "churn_risk": [0.15, 0.15, 0.15],
        }
    )

    forecast = forecast_revenue(df, periods=3)

    assert len(forecast) == 6
    assert forecast["series"].tolist().count("Forecast") == 3
    assert {"lower_bound", "upper_bound"}.issubset(forecast.columns)
    assert forecast_summary(forecast).startswith("The directional forecast")
