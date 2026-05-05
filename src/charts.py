"""Plotly chart builders for the Retail KPI & Forecasting Sandbox dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import BRAND_COLORS, CHART_COLORS
from src.utils import safe_divide


CURRENCY_TICK = "$,.0f"
PERCENT_TICK = ".0%"


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16, color=BRAND_COLORS["muted"]),
    )
    return apply_chart_theme(fig, height=340)


def apply_chart_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    """Apply a consistent review-ready visual theme to Plotly figures."""

    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=42, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.66)",
        font=dict(color=BRAND_COLORS["ink"], family="Georgia, Times New Roman, serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor=BRAND_COLORS["border"])
    fig.update_yaxes(gridcolor="rgba(102,112,107,0.16)", zerolinecolor=BRAND_COLORS["border"])
    return fig


def metric_trend_chart(
    trends: pd.DataFrame,
    metrics: dict[str, str],
    title: str,
    yaxis_title: str = "Amount",
    tickformat: str | None = None,
    height: int = 430,
) -> go.Figure:
    """Create a multi-line trend chart from monthly KPI data."""

    if trends.empty:
        return _empty_figure("No trend data is available for the current filters.")

    value_vars = [col for col in metrics if col in trends.columns]
    long_df = trends.melt(
        id_vars="month",
        value_vars=value_vars,
        var_name="metric",
        value_name="value",
    )
    long_df["Metric"] = long_df["metric"].map(metrics)
    fig = px.line(
        long_df,
        x="month",
        y="value",
        color="Metric",
        markers=True,
        color_discrete_sequence=CHART_COLORS,
        title=title,
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_layout(yaxis_title=yaxis_title, xaxis_title="Month")
    if tickformat:
        fig.update_yaxes(tickformat=tickformat)
    return apply_chart_theme(fig, height=height)


def performance_bar_chart(
    performance: pd.DataFrame,
    dimension: str,
    metric: str,
    title: str,
    height: int = 390,
) -> go.Figure:
    """Create a ranked performance bar chart."""

    if performance.empty:
        return _empty_figure("No performance data is available for the current filters.")

    label = dimension.replace("_", " ").title()
    metric_label = metric.replace("_", " ").title()
    fig = px.bar(
        performance,
        x=dimension,
        y=metric,
        color="gross_margin_rate",
        color_continuous_scale=[BRAND_COLORS["orange"], "#dfc176", BRAND_COLORS["green"]],
        text_auto=".2s",
        title=title,
    )
    fig.update_layout(
        xaxis_title=label,
        yaxis_title=metric_label,
        coloraxis_colorbar_title="Gross Margin",
    )
    fig.update_traces(marker_line_width=0, textposition="outside")
    return apply_chart_theme(fig, height=height)


def actual_vs_forecast_chart(forecast_df: pd.DataFrame, title: str = "Actual Revenue vs Forecast") -> go.Figure:
    """Create an actual-vs-forecast chart with an uncertainty band."""

    if forecast_df.empty:
        return _empty_figure("Not enough data is available to forecast revenue.")

    fig = px.line(
        forecast_df,
        x="month",
        y="revenue",
        color="series",
        markers=True,
        color_discrete_map={"Historical": BRAND_COLORS["green"], "Forecast": BRAND_COLORS["orange"]},
        title=title,
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    forecast_only = forecast_df[forecast_df["series"] == "Forecast"].copy()
    if not forecast_only.empty:
        fig.add_scatter(
            x=forecast_only["month"],
            y=forecast_only["upper_bound"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
        fig.add_scatter(
            x=forecast_only["month"],
            y=forecast_only["lower_bound"],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(184, 92, 43, 0.16)",
            line=dict(width=0),
            name="Planning range",
            hoverinfo="skip",
        )
    fig.update_layout(yaxis_title="Revenue", xaxis_title="Month")
    fig.update_yaxes(tickformat=CURRENCY_TICK)
    return apply_chart_theme(fig, height=460)


def scenario_impact_chart(scenario_result: dict[str, float | str]) -> go.Figure:
    """Show revenue, profit, and gross margin deltas for a scenario."""

    if not scenario_result:
        return _empty_figure("Run a scenario to see estimated impact.")

    df = pd.DataFrame(
        [
            {"Metric": "Revenue", "Delta": float(scenario_result["revenue_delta"])},
            {"Metric": "Profit", "Delta": float(scenario_result["profit_delta"])},
            {"Metric": "Gross Margin", "Delta": float(scenario_result["gross_margin_delta"])},
        ]
    )
    df["Direction"] = df["Delta"].apply(lambda value: "Positive" if value >= 0 else "Negative")
    fig = px.bar(
        df,
        x="Metric",
        y="Delta",
        color="Direction",
        color_discrete_map={"Positive": BRAND_COLORS["green"], "Negative": BRAND_COLORS["red"]},
        text_auto=".2s",
        title="Estimated Scenario Impact",
    )
    fig.update_layout(yaxis_title="Estimated delta", xaxis_title="")
    fig.update_yaxes(tickformat=CURRENCY_TICK)
    fig.update_traces(textposition="outside")
    return apply_chart_theme(fig, height=370)


def retention_by_segment_chart(df: pd.DataFrame) -> go.Figure:
    """Create a customer-segment retention chart."""

    if df.empty:
        return _empty_figure("No retention data is available for the current filters.")

    grouped = (
        df.groupby("customer_segment", as_index=False)
        .agg(
            retained_units=("retention_rate", lambda values: float((values * df.loc[values.index, "units_sold"]).sum())),
            units_sold=("units_sold", "sum"),
        )
        .sort_values("retained_units", ascending=False)
    )
    grouped["retention_rate"] = grouped.apply(
        lambda row: safe_divide(float(row["retained_units"]), float(row["units_sold"])),
        axis=1,
    )
    fig = px.bar(
        grouped,
        x="customer_segment",
        y="retention_rate",
        color="retention_rate",
        color_continuous_scale=[BRAND_COLORS["orange"], BRAND_COLORS["green"]],
        text_auto=".1%",
        title="Retention by Customer Segment",
    )
    fig.update_yaxes(tickformat=PERCENT_TICK, range=[0, 1])
    fig.update_layout(xaxis_title="Customer Segment", yaxis_title="Retention Rate", showlegend=False)
    return apply_chart_theme(fig, height=360)
