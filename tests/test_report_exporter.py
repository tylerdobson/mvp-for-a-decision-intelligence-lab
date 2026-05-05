from __future__ import annotations

import pandas as pd

from src.report_exporter import (
    dataframe_to_csv_bytes,
    executive_summary_markdown,
    kpi_summary_frame,
    recommendations_frame,
    scenario_frame,
)


def test_export_helpers_create_expected_shapes() -> None:
    kpis = {
        "revenue": 1000.0,
        "profit": 100.0,
        "gross_margin_rate": 0.50,
        "profit_margin": 0.10,
        "operating_cost": 250.0,
        "marketing_spend": 150.0,
        "units_sold": 10.0,
        "average_price": 100.0,
        "retention_rate": 0.85,
        "churn_risk": 0.15,
        "revenue_mom_pct": 5.0,
        "profit_mom_pct": 6.0,
        "best_region": "Northeast",
        "worst_region": "West",
        "best_category": "Software",
        "worst_category": "Services",
    }
    recommendations = [
        {
            "priority": "High",
            "theme": "Margin",
            "recommendation": "Review margin pressure.",
            "evidence": "Profit margin is below target.",
            "action": "Audit costs.",
        }
    ]
    scenario = {"risk_level": "Low", "revenue_delta_pct": 3.0, "profit_delta_pct": 4.0, "recommended_action": "Pilot."}

    assert dataframe_to_csv_bytes(pd.DataFrame({"a": [1]})).startswith(b"a")
    assert "Revenue" in set(kpi_summary_frame(kpis)["metric"])
    assert recommendations_frame(recommendations).shape == (1, 5)
    assert scenario_frame(scenario).shape[0] == 4
    assert "Retail KPI & Forecasting Sandbox Executive Summary" in executive_summary_markdown(kpis, recommendations, scenario)
