"""Streamlit dashboard for Decision Intelligence Lab."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import filter_business_data, get_filter_options, load_business_data
from src.forecasting import forecast_revenue, forecast_summary
from src.kpi_engine import calculate_kpis, monthly_trends, performance_by_dimension
from src.recommendation_engine import generate_recommendations
from src.scenario_engine import run_scenario
from src.utils import (
    format_currency,
    format_delta_pct,
    format_number,
    format_percentage,
)


st.set_page_config(
    page_title="Decision Intelligence Lab",
    page_icon="DIL",
    layout="wide",
)


CUSTOM_CSS = """
<style>
    :root {
        --dil-bg: #f5f1e8;
        --dil-ink: #17201b;
        --dil-muted: #66706b;
        --dil-panel: #fffaf0;
        --dil-border: #ded3bf;
        --dil-accent: #0f6b5f;
        --dil-warn: #b85c2b;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(15, 107, 95, 0.11), transparent 32rem),
            linear-gradient(180deg, #f7f1e6 0%, #f4efe6 42%, #efe9df 100%);
        color: var(--dil-ink);
    }

    h1, h2, h3 {
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: -0.03em;
    }

    [data-testid="stSidebar"] {
        background: #efe6d7;
        border-right: 1px solid var(--dil-border);
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 250, 240, 0.82);
        border: 1px solid var(--dil-border);
        border-radius: 18px;
        padding: 18px 18px 14px;
        box-shadow: 0 18px 42px rgba(52, 41, 27, 0.08);
    }

    div[data-testid="stMetricLabel"] p {
        color: var(--dil-muted);
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .dil-hero {
        border: 1px solid var(--dil-border);
        border-radius: 28px;
        padding: 30px 34px;
        background:
            linear-gradient(135deg, rgba(255,250,240,0.96), rgba(227, 240, 230, 0.84)),
            repeating-linear-gradient(90deg, rgba(15,107,95,0.06) 0 1px, transparent 1px 52px);
        box-shadow: 0 22px 55px rgba(52, 41, 27, 0.10);
        margin-bottom: 18px;
    }

    .dil-hero p {
        color: var(--dil-muted);
        max-width: 850px;
        font-size: 1.06rem;
        line-height: 1.65;
    }

    .dil-callout {
        border-left: 5px solid var(--dil-accent);
        background: rgba(255,250,240,0.78);
        padding: 18px 20px;
        border-radius: 14px;
        margin: 12px 0 18px;
    }

    .priority-high {
        border-left: 5px solid #a73d2a;
    }

    .priority-medium {
        border-left: 5px solid #bd7b21;
    }

    .priority-low {
        border-left: 5px solid #0f6b5f;
    }
</style>
"""


@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    """Load dashboard data from SQLite."""

    return load_business_data()


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    st.metric(label=label, value=value, delta=delta)


def plot_trend_chart(trends: pd.DataFrame):
    long_df = trends.melt(
        id_vars="month",
        value_vars=["revenue", "profit", "operating_cost", "marketing_spend"],
        var_name="Metric",
        value_name="Amount",
    )
    long_df["Metric"] = long_df["Metric"].str.replace("_", " ").str.title()
    fig = px.line(
        long_df,
        x="month",
        y="Amount",
        color="Metric",
        markers=True,
        color_discrete_sequence=["#0f6b5f", "#233d70", "#b85c2b", "#8f6a16"],
    )
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Amount ($)",
        xaxis_title="Month",
        legend_title_text="Metric",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    return fig


def plot_margin_chart(trends: pd.DataFrame):
    margin_df = trends.melt(
        id_vars="month",
        value_vars=["gross_margin_rate", "profit_margin"],
        var_name="Metric",
        value_name="Rate",
    )
    margin_df["Metric"] = margin_df["Metric"].str.replace("_", " ").str.title()
    fig = px.line(
        margin_df,
        x="month",
        y="Rate",
        color="Metric",
        markers=True,
        color_discrete_sequence=["#0f6b5f", "#a73d2a"],
    )
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Rate",
        xaxis_title="Month",
        legend_title_text="Metric",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    return fig


def plot_performance_bar(df: pd.DataFrame, dimension: str, metric: str):
    perf = performance_by_dimension(df, dimension, sort_by=metric)
    fig = px.bar(
        perf,
        x=dimension,
        y=metric,
        color="gross_margin_rate",
        color_continuous_scale=["#c86737", "#dfc176", "#0f6b5f"],
        text_auto=".2s",
    )
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title=dimension.replace("_", " ").title(),
        yaxis_title=metric.replace("_", " ").title(),
        coloraxis_colorbar_title="Gross Margin",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    return fig


def render_recommendation_card(rec: dict[str, str]) -> None:
    priority_class = rec["priority"].lower()
    st.markdown(
        f"""
        <div class="dil-callout priority-{priority_class}">
            <strong>{rec['priority']} Priority - {rec['theme']}</strong><br>
            {rec['recommendation']}<br>
            <span style="color:#66706b;">Reason: {rec['reason']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

data = get_data()
options = get_filter_options(data)

st.sidebar.title("Decision Controls")
selected_regions = st.sidebar.multiselect(
    "Region",
    options["regions"],
    default=options["regions"],
)
selected_categories = st.sidebar.multiselect(
    "Product category",
    options["product_categories"],
    default=options["product_categories"],
)
selected_segments = st.sidebar.multiselect(
    "Customer segment",
    options["customer_segments"],
    default=options["customer_segments"],
)
date_range = st.sidebar.date_input(
    "Date range",
    value=(options["min_date"], options["max_date"]),
    min_value=options["min_date"],
    max_value=options["max_date"],
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = options["min_date"], options["max_date"]

filtered_data = filter_business_data(
    data,
    regions=selected_regions,
    product_categories=selected_categories,
    customer_segments=selected_segments,
    start_date=start_date,
    end_date=end_date,
)

if filtered_data.empty:
    st.warning("No records match the current filters. Adjust the sidebar controls.")
    st.stop()

kpis = calculate_kpis(filtered_data)
trends = monthly_trends(filtered_data)

st.markdown(
    """
    <div class="dil-hero">
        <h1>Decision Intelligence Lab</h1>
        <p>
            A reusable analytics dashboard that turns operational business data into KPIs,
            forecasts, scenario analysis, and executive recommendations. The goal is not
            just to show charts. The goal is to help answer what decision should be made next.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

overview_tab, explorer_tab, forecast_tab, scenario_tab, recommendations_tab = st.tabs(
    [
        "Executive Overview",
        "KPI Explorer",
        "Forecasting",
        "Scenario Analysis",
        "Executive Recommendations",
    ]
)

with overview_tab:
    st.subheader("Executive Overview")
    metric_cols = st.columns(5)
    with metric_cols[0]:
        metric_card("Revenue", format_currency(float(kpis["revenue"])), format_delta_pct(float(kpis["revenue_mom_pct"])))
    with metric_cols[1]:
        metric_card("Profit", format_currency(float(kpis["profit"])), format_delta_pct(float(kpis["profit_mom_pct"])))
    with metric_cols[2]:
        metric_card("Gross Margin", format_percentage(float(kpis["gross_margin_rate"])))
    with metric_cols[3]:
        metric_card("Operating Cost", format_currency(float(kpis["operating_cost"])))
    with metric_cols[4]:
        metric_card("Units Sold", format_number(float(kpis["units_sold"])))

    st.markdown(
        f"""
        <div class="dil-callout">
            <strong>Decision signal:</strong>
            Best region is <strong>{kpis['best_region']}</strong>, weakest region is
            <strong>{kpis['worst_region']}</strong>. Best category is
            <strong>{kpis['best_category']}</strong>, weakest category is
            <strong>{kpis['worst_category']}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_col, margin_col = st.columns([1.35, 1])
    with chart_col:
        st.plotly_chart(plot_trend_chart(trends), use_container_width=True)
    with margin_col:
        st.plotly_chart(plot_margin_chart(trends), use_container_width=True)

with explorer_tab:
    st.subheader("KPI Explorer")
    st.caption("Use the sidebar filters to isolate regions, categories, segments, and time periods.")

    summary_cols = st.columns(4)
    with summary_cols[0]:
        metric_card("Profit Margin", format_percentage(float(kpis["profit_margin"])))
    with summary_cols[1]:
        metric_card("Marketing Efficiency", f"{float(kpis['marketing_efficiency']):.1f}x")
    with summary_cols[2]:
        metric_card("Avg. Price", format_currency(float(kpis["average_price"])))
    with summary_cols[3]:
        metric_card("Retention", format_percentage(float(kpis["retention_rate"])))

    region_col, category_col = st.columns(2)
    with region_col:
        st.markdown("#### Region Performance")
        st.plotly_chart(
            plot_performance_bar(filtered_data, "region", "profit"),
            use_container_width=True,
        )
    with category_col:
        st.markdown("#### Product Category Performance")
        st.plotly_chart(
            plot_performance_bar(filtered_data, "product_category", "revenue"),
            use_container_width=True,
        )

    st.markdown("#### Filtered Data Preview")
    preview_columns = [
        "month",
        "region",
        "product_category",
        "customer_segment",
        "revenue",
        "profit",
        "gross_margin_rate",
        "retention_rate",
    ]
    st.dataframe(
        filtered_data[preview_columns].sort_values("month", ascending=False).head(25),
        use_container_width=True,
        hide_index=True,
    )

with forecast_tab:
    st.subheader("Forecasting")
    forecast_periods = st.slider("Forecast horizon in months", 3, 6, 6)
    forecast_df = forecast_revenue(filtered_data, periods=forecast_periods)
    forecast_only = forecast_df[forecast_df["series"] == "Forecast"].copy()

    fig = px.line(
        forecast_df,
        x="month",
        y="revenue",
        color="series",
        markers=True,
        color_discrete_map={"Historical": "#0f6b5f", "Forecast": "#b85c2b"},
    )
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
            name="Forecast uncertainty band",
            hoverinfo="skip",
        )
    fig.update_layout(
        height=440,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Revenue ($)",
        xaxis_title="Month",
        legend_title_text="Series",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"<div class='dil-callout'>{forecast_summary(forecast_df)}</div>", unsafe_allow_html=True)
    st.dataframe(
        forecast_only[["month", "revenue", "lower_bound", "upper_bound"]],
        use_container_width=True,
        hide_index=True,
    )

with scenario_tab:
    st.subheader("Scenario Analysis")
    st.caption("Adjust assumptions to estimate directional impact. This is a planning model, not a guarantee.")

    scenario_cols = st.columns(4)
    with scenario_cols[0]:
        marketing_change = st.slider("Marketing spend change", -40, 50, 10, format="%d%%")
    with scenario_cols[1]:
        price_change = st.slider("Price change", -25, 30, 0, format="%d%%")
    with scenario_cols[2]:
        cost_change = st.slider("Cost change", -25, 35, 0, format="%d%%")
    with scenario_cols[3]:
        demand_change = st.slider("Demand change", -30, 40, 5, format="%d%%")

    scenario_result = run_scenario(
        kpis,
        marketing_change_pct=marketing_change,
        price_change_pct=price_change,
        cost_change_pct=cost_change,
        demand_change_pct=demand_change,
    )

    impact_cols = st.columns(4)
    with impact_cols[0]:
        metric_card(
            "Estimated Revenue",
            format_currency(float(scenario_result["adjusted_revenue"])),
            format_delta_pct(float(scenario_result["revenue_delta_pct"])),
        )
    with impact_cols[1]:
        metric_card(
            "Estimated Profit",
            format_currency(float(scenario_result["adjusted_profit"])),
            format_delta_pct(float(scenario_result["profit_delta_pct"])),
        )
    with impact_cols[2]:
        metric_card(
            "Gross Margin",
            format_percentage(float(scenario_result["adjusted_gross_margin_rate"])),
            format_delta_pct(float(scenario_result["gross_margin_delta_pct"])),
        )
    with impact_cols[3]:
        metric_card("Risk Level", str(scenario_result["risk_level"]))

    st.markdown(
        f"""
        <div class="dil-callout">
            <strong>Recommended action:</strong> {scenario_result['recommended_action']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Scenario assumptions"):
        st.write(
            "- A 1% marketing spend increase is modeled as a 0.25% demand lift before other changes."
        )
        st.write("- A 1% price increase is modeled as a 0.35% demand reduction.")
        st.write("- Cost changes affect cost of goods and operating cost.")
        st.write("- Results are directional and should be validated with real experiments.")

with recommendations_tab:
    st.subheader("Executive Recommendations")
    st.caption("Recommendations are rule-based, explainable, and tied to the selected data and scenario.")
    recommendations = generate_recommendations(filtered_data, kpis, scenario_result)
    for recommendation in recommendations:
        render_recommendation_card(recommendation)
