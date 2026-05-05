"""Export helpers for dashboard data and executive summaries."""

from __future__ import annotations

from datetime import datetime
from io import StringIO

import pandas as pd

from src.utils import format_currency, format_delta_pct, format_number, format_percentage


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to CSV bytes for Streamlit download buttons."""

    return df.to_csv(index=False).encode("utf-8")


def kpi_summary_frame(kpis: dict[str, float | str]) -> pd.DataFrame:
    """Turn KPI values into a tidy export table."""

    rows = [
        ("Revenue", format_currency(float(kpis["revenue"]))),
        ("Profit", format_currency(float(kpis["profit"]))),
        ("Gross Margin Rate", format_percentage(float(kpis["gross_margin_rate"]))),
        ("Profit Margin", format_percentage(float(kpis["profit_margin"]))),
        ("Operating Cost", format_currency(float(kpis["operating_cost"]))),
        ("Marketing Spend", format_currency(float(kpis["marketing_spend"]))),
        ("Units Sold", format_number(float(kpis["units_sold"]))),
        ("Average Price", format_currency(float(kpis["average_price"]))),
        ("Retention Rate", format_percentage(float(kpis["retention_rate"]))),
        ("Churn Risk", format_percentage(float(kpis["churn_risk"]))),
        ("Revenue MoM", format_delta_pct(float(kpis["revenue_mom_pct"]))),
        ("Profit MoM", format_delta_pct(float(kpis["profit_mom_pct"]))),
        ("Best Region", str(kpis["best_region"])),
        ("Weakest Region", str(kpis["worst_region"])),
        ("Best Category", str(kpis["best_category"])),
        ("Weakest Category", str(kpis["worst_category"])),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def recommendations_frame(recommendations: list[dict[str, str]]) -> pd.DataFrame:
    """Create an export table for recommendations."""

    columns = ["priority", "theme", "recommendation", "evidence", "action"]
    if not recommendations:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(recommendations)[columns]


def scenario_frame(scenario_result: dict[str, float | str]) -> pd.DataFrame:
    """Create an export table for scenario output."""

    return pd.DataFrame(
        [{"metric": key, "value": value} for key, value in scenario_result.items()]
    )


def executive_summary_markdown(
    kpis: dict[str, float | str],
    recommendations: list[dict[str, str]],
    scenario_result: dict[str, float | str] | None = None,
) -> str:
    """Build a concise Markdown executive summary for download."""

    buffer = StringIO()
    buffer.write("# Retail KPI & Forecasting Sandbox Executive Summary\n\n")
    buffer.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    buffer.write("## KPI Snapshot\n\n")
    buffer.write(f"- Revenue: {format_currency(float(kpis['revenue']))}\n")
    buffer.write(f"- Profit: {format_currency(float(kpis['profit']))}\n")
    buffer.write(f"- Gross margin: {format_percentage(float(kpis['gross_margin_rate']))}\n")
    buffer.write(f"- Profit margin: {format_percentage(float(kpis['profit_margin']))}\n")
    buffer.write(f"- Revenue month-over-month: {format_delta_pct(float(kpis['revenue_mom_pct']))}\n")
    buffer.write(f"- Profit month-over-month: {format_delta_pct(float(kpis['profit_mom_pct']))}\n")
    buffer.write(f"- Strongest region: {kpis['best_region']}\n")
    buffer.write(f"- Weakest region: {kpis['worst_region']}\n\n")

    if scenario_result:
        buffer.write("## Scenario Snapshot\n\n")
        buffer.write(f"- Estimated revenue impact: {format_delta_pct(float(scenario_result['revenue_delta_pct']))}\n")
        buffer.write(f"- Estimated profit impact: {format_delta_pct(float(scenario_result['profit_delta_pct']))}\n")
        buffer.write(f"- Risk level: {scenario_result['risk_level']}\n")
        buffer.write(f"- Recommended action: {scenario_result['recommended_action']}\n\n")

    buffer.write("## Recommendations\n\n")
    for rec in recommendations:
        buffer.write(f"### {rec['priority']} - {rec['theme']}\n")
        buffer.write(f"- Recommendation: {rec['recommendation']}\n")
        buffer.write(f"- Evidence: {rec['evidence']}\n")
        buffer.write(f"- Action: {rec['action']}\n\n")

    buffer.write("## Limitation\n\n")
    buffer.write(
        "This summary uses modeled demo data and directional models. "
        "It is decision support, not a guaranteed prediction.\n"
    )
    return buffer.getvalue()


def markdown_to_bytes(markdown: str) -> bytes:
    """Encode Markdown text for download."""

    return markdown.encode("utf-8")
