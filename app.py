"""Streamlit dashboard for Retail KPI & Forecasting Sandbox."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import (
    CURRENCY_TICK,
    PERCENT_TICK,
    actual_vs_forecast_chart,
    metric_trend_chart,
    performance_bar_chart,
    retention_by_segment_chart,
    scenario_impact_chart,
)
from src.config import (
    APP_SUMMARY,
    APP_TITLE,
    DEFAULT_SCENARIO,
    NAV_SECTIONS,
    SECTION_BY_SLUG,
    SECTION_LABELS,
)
from src.data_loader import filter_business_data, get_filter_options, load_business_data
from src.forecasting import forecast_revenue, forecast_summary
from src.kpi_engine import calculate_kpis, monthly_trends, performance_by_dimension
from src.recommendation_engine import generate_recommendations
from src.report_exporter import (
    dataframe_to_csv_bytes,
    executive_summary_markdown,
    kpi_summary_frame,
    markdown_to_bytes,
    recommendations_frame,
    scenario_frame,
)
from src.scenario_engine import run_scenario
from src.ui_components import (
    apply_page_style,
    render_callout,
    render_empty_state,
    render_hero,
    render_insight_cards,
    render_metric_row,
    render_recommendation_card,
    render_section_header,
)
from src.utils import format_currency, format_delta_pct, format_number, format_percentage


st.set_page_config(page_title=APP_TITLE, page_icon="DIL", layout="wide")
apply_page_style()


@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    """Load dashboard data from SQLite."""

    return load_business_data()


def _query_section_slug() -> str | None:
    value = st.query_params.get("section", None)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _section_index_from_query() -> int:
    slug = _query_section_slug()
    if slug in SECTION_BY_SLUG:
        return [section.slug for section in NAV_SECTIONS].index(slug)
    return 0


def _render_sidebar(data: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    options = get_filter_options(data)
    st.sidebar.title("Retail KPI Sandbox")
    st.sidebar.caption("Filter the modeled retail operating data, then move through the decision workflow.")

    section_label = st.sidebar.radio(
        "Navigate",
        SECTION_LABELS,
        index=_section_index_from_query(),
    )

    st.sidebar.divider()
    st.sidebar.subheader("Filters")
    selected_regions = st.sidebar.multiselect("Region", options["regions"], default=options["regions"])
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

    filtered = filter_business_data(
        data,
        regions=selected_regions,
        product_categories=selected_categories,
        customer_segments=selected_segments,
        start_date=start_date,
        end_date=end_date,
    )

    st.sidebar.divider()
    st.sidebar.subheader("Data health")
    st.sidebar.metric("Filtered records", f"{len(filtered):,}")
    if not filtered.empty:
        st.sidebar.caption(
            f"Filtered window: {filtered['month'].min().date()} to {filtered['month'].max().date()}"
        )
    st.sidebar.caption("Modeled retail data is safe for public demos.")
    return section_label, filtered


def _build_executive_insights(kpis: dict[str, float | str], trends: pd.DataFrame) -> list[dict[str, str]]:
    revenue_mom = float(kpis["revenue_mom_pct"])
    profit_mom = float(kpis["profit_mom_pct"])
    margin = float(kpis["gross_margin_rate"])
    churn = float(kpis["churn_risk"])

    trend_body = (
        f"Revenue moved {format_delta_pct(revenue_mom)} month over month while "
        f"profit moved {format_delta_pct(profit_mom)}."
    )
    if profit_mom < revenue_mom - 5:
        trend_body += " Profit is lagging revenue, so cost control deserves attention."
    else:
        trend_body += " The profit trend is not materially worse than revenue."

    latest_units = 0.0 if trends.empty else float(trends.iloc[-1]["units_sold"])
    return [
        {"title": "Trend signal", "body": trend_body},
        {
            "title": "Portfolio economics",
            "body": f"Gross margin is {format_percentage(margin)} and latest monthly unit volume is {format_number(latest_units)}.",
        },
        {
            "title": "Customer risk",
            "body": f"Weighted churn risk is {format_percentage(churn)}. Treat retention as a decision input, not just a lagging metric.",
        },
    ]


def _format_display_table(df: pd.DataFrame) -> pd.DataFrame:
    display = df.copy()
    display["month"] = pd.to_datetime(display["month"]).dt.strftime("%Y-%m")
    return display


def render_executive_overview(
    filtered_data: pd.DataFrame,
    kpis: dict[str, float | str],
    trends: pd.DataFrame,
) -> None:
    render_section_header(
        "Executive Overview",
        "A landing page for the most important decision signals in the selected business slice.",
    )
    render_metric_row(kpis)
    render_callout(
        "Recommended next action",
        (
            f"Start with {kpis['best_region']} and {kpis['best_category']} as the strongest operating areas, "
            f"then investigate {kpis['worst_region']} and {kpis['worst_category']} before increasing broad spend."
        ),
    )
    render_insight_cards(_build_executive_insights(kpis, trends))

    left, right = st.columns([1.35, 1])
    with left:
        st.plotly_chart(
            metric_trend_chart(
                trends,
                {"revenue": "Revenue", "profit": "Profit", "operating_cost": "Operating Cost"},
                "Monthly Revenue, Profit, and Operating Cost",
                "Amount",
                CURRENCY_TICK,
            ),
            width="stretch",
        )
    with right:
        region_perf = performance_by_dimension(filtered_data, "region")
        st.plotly_chart(
            performance_bar_chart(region_perf, "region", "profit", "Region Profit Ranking"),
            width="stretch",
        )


def render_kpi_explorer(
    filtered_data: pd.DataFrame,
    kpis: dict[str, float | str],
    trends: pd.DataFrame,
) -> None:
    render_section_header(
        "KPI Explorer",
        "Inspect the filtered KPI profile and identify what changed across revenue, profit, margin, cost, and units.",
    )
    cards = st.columns(5)
    cards[0].metric("Profit Margin", format_percentage(float(kpis["profit_margin"])))
    cards[1].metric("Marketing Efficiency", f"{float(kpis['marketing_efficiency']):.1f}x")
    cards[2].metric("Average Price", format_currency(float(kpis["average_price"])))
    cards[3].metric("Retention", format_percentage(float(kpis["retention_rate"])))
    cards[4].metric("Records", f"{len(filtered_data):,}")

    latest_change = "No prior month is available for comparison."
    if len(trends) >= 2:
        latest = trends.iloc[-1]
        latest_change = (
            f"Latest month revenue moved {format_delta_pct(float(latest['revenue_mom_pct']))} "
            f"and profit moved {format_delta_pct(float(latest['profit_mom_pct']))}."
        )
    render_callout("What changed", latest_change)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            metric_trend_chart(
                trends,
                {"revenue": "Revenue", "profit": "Profit"},
                "Revenue and Profit Trend",
                "Amount",
                CURRENCY_TICK,
            ),
            width="stretch",
        )
        st.plotly_chart(retention_by_segment_chart(filtered_data), width="stretch")
    with right:
        st.plotly_chart(
            metric_trend_chart(
                trends,
                {"gross_margin_rate": "Gross Margin", "profit_margin": "Profit Margin"},
                "Margin Trend",
                "Rate",
                PERCENT_TICK,
            ),
            width="stretch",
        )
        st.plotly_chart(
            metric_trend_chart(trends, {"units_sold": "Units Sold"}, "Units Trend", "Units"),
            width="stretch",
        )


def render_trends(filtered_data: pd.DataFrame, trends: pd.DataFrame) -> None:
    render_section_header(
        "Revenue & Profit Trends",
        "Portfolio-ready trend charts designed to make cost, margin, and growth patterns visible.",
    )
    st.plotly_chart(
        metric_trend_chart(
            trends,
            {
                "revenue": "Revenue",
                "gross_margin": "Gross Margin",
                "profit": "Profit",
                "operating_cost": "Operating Cost",
                "marketing_spend": "Marketing Spend",
            },
            "Monthly Financial Trend",
            "Amount",
            CURRENCY_TICK,
            height=500,
        ),
        width="stretch",
    )
    left, right = st.columns(2)
    with left:
        category_perf = performance_by_dimension(filtered_data, "product_category")
        st.plotly_chart(
            performance_bar_chart(category_perf, "product_category", "revenue", "Product Category Revenue Ranking"),
            width="stretch",
        )
    with right:
        segment_perf = performance_by_dimension(filtered_data, "customer_segment")
        st.plotly_chart(
            performance_bar_chart(segment_perf, "customer_segment", "profit", "Customer Segment Profit Ranking"),
            width="stretch",
        )


def render_forecasting_lab(filtered_data: pd.DataFrame) -> None:
    render_section_header(
        "Forecasting Lab",
        "A transparent directional forecast using a blended linear trend and recent moving average.",
    )
    horizon = st.slider("Forecast horizon", min_value=3, max_value=6, value=6, format="%d months")
    forecast_df = forecast_revenue(filtered_data, periods=horizon)
    st.plotly_chart(actual_vs_forecast_chart(forecast_df), width="stretch")
    render_callout("Plain-English forecast", forecast_summary(forecast_df))
    render_callout(
        "Uncertainty note",
        "The forecast is designed for planning discussion. It is not a guaranteed prediction and should be validated with actual results.",
    )
    forecast_only = forecast_df[forecast_df["series"] == "Forecast"].copy()
    if not forecast_only.empty:
        forecast_only["month"] = forecast_only["month"].dt.strftime("%Y-%m")
        st.dataframe(
            forecast_only[["month", "revenue", "lower_bound", "upper_bound"]],
            width="stretch",
            hide_index=True,
            column_config={
                "revenue": st.column_config.NumberColumn("Forecast Revenue", format="$%.0f"),
                "lower_bound": st.column_config.NumberColumn("Lower Planning Range", format="$%.0f"),
                "upper_bound": st.column_config.NumberColumn("Upper Planning Range", format="$%.0f"),
            },
        )


def render_scenario_analysis(kpis: dict[str, float | str]) -> dict[str, float | str]:
    render_section_header(
        "Scenario Analysis",
        "Adjust business assumptions and translate the estimated impact into a recommended action.",
    )
    controls = st.columns(5)
    marketing_change = controls[0].slider("Marketing spend", -40, 50, DEFAULT_SCENARIO["marketing_change_pct"], format="%d%%")
    price_change = controls[1].slider("Price", -25, 30, DEFAULT_SCENARIO["price_change_pct"], format="%d%%")
    cost_change = controls[2].slider("Cost", -25, 35, DEFAULT_SCENARIO["cost_change_pct"], format="%d%%")
    demand_change = controls[3].slider("Demand", -30, 40, DEFAULT_SCENARIO["demand_change_pct"], format="%d%%")
    retention_change = controls[4].slider("Retention", -15, 20, DEFAULT_SCENARIO["retention_change_pct"], format="%d%%")

    scenario_result = run_scenario(
        kpis,
        marketing_change_pct=marketing_change,
        price_change_pct=price_change,
        cost_change_pct=cost_change,
        demand_change_pct=demand_change,
        retention_change_pct=retention_change,
    )

    output_cols = st.columns(5)
    output_cols[0].metric(
        "Estimated Revenue",
        format_currency(float(scenario_result["adjusted_revenue"])),
        format_delta_pct(float(scenario_result["revenue_delta_pct"])),
    )
    output_cols[1].metric(
        "Estimated Profit",
        format_currency(float(scenario_result["adjusted_profit"])),
        format_delta_pct(float(scenario_result["profit_delta_pct"])),
    )
    output_cols[2].metric(
        "Gross Margin",
        format_percentage(float(scenario_result["adjusted_gross_margin_rate"])),
        format_delta_pct(float(scenario_result["gross_margin_delta_pct"])),
    )
    output_cols[3].metric(
        "Retention",
        format_percentage(float(scenario_result["adjusted_retention_rate"])),
        format_delta_pct(float(scenario_result["retention_delta_pct"])),
    )
    output_cols[4].metric("Risk Level", str(scenario_result["risk_level"]))

    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(scenario_impact_chart(scenario_result), width="stretch")
    with right:
        render_callout("Recommended action", str(scenario_result["recommended_action"]))
        render_callout("Business interpretation", str(scenario_result["interpretation"]))

    with st.expander("Scenario assumptions"):
        st.write("- A 1% marketing spend increase is modeled as a 0.25% demand lift before other changes.")
        st.write("- A 1% price increase is modeled as a 0.35% demand reduction.")
        st.write("- A 1% retention increase is modeled as a 0.15% demand lift from healthier customer economics.")
        st.write("- Cost changes affect cost of goods and operating cost.")
        st.write("- Results are directional estimates for decision support, not guaranteed outcomes.")
    return scenario_result


def render_recommendations(
    filtered_data: pd.DataFrame,
    kpis: dict[str, float | str],
    scenario_result: dict[str, float | str],
) -> list[dict[str, str]]:
    render_section_header(
        "Executive Recommendations",
        "Explainable recommendation cards with priority, evidence, and suggested action.",
    )
    recommendations = generate_recommendations(filtered_data, kpis, scenario_result)
    for recommendation in recommendations:
        render_recommendation_card(recommendation)
    return recommendations


def render_data_explorer(filtered_data: pd.DataFrame) -> None:
    render_section_header(
        "Data Explorer",
        "A clean view of the filtered modeled retail data. Use exports for deeper analysis.",
    )
    search = st.text_input("Search region, category, or segment", "")
    table = filtered_data.copy()
    if search:
        mask = (
            table["region"].str.contains(search, case=False, na=False)
            | table["product_category"].str.contains(search, case=False, na=False)
            | table["customer_segment"].str.contains(search, case=False, na=False)
        )
        table = table[mask]

    render_callout("Dataset note", "This is deterministic modeled retail data created for public demonstration.")
    display = _format_display_table(table).sort_values("month", ascending=False)
    st.dataframe(
        display.head(250),
        width="stretch",
        hide_index=True,
        column_config={
            "revenue": st.column_config.NumberColumn("Revenue", format="$%.0f"),
            "profit": st.column_config.NumberColumn("Profit", format="$%.0f"),
            "gross_margin_rate": st.column_config.NumberColumn("Gross Margin", format="%.1f%%"),
            "retention_rate": st.column_config.NumberColumn("Retention", format="%.1f%%"),
            "churn_risk": st.column_config.NumberColumn("Churn Risk", format="%.1f%%"),
        },
    )
    st.caption(f"Showing up to 250 rows from {len(table):,} filtered records.")
    st.download_button(
        "Download filtered dataset CSV",
        data=dataframe_to_csv_bytes(table),
        file_name="decision_lab_filtered_data.csv",
        mime="text/csv",
    )


def render_export_center(
    filtered_data: pd.DataFrame,
    kpis: dict[str, float | str],
    recommendations: list[dict[str, str]],
    scenario_result: dict[str, float | str],
) -> None:
    render_section_header(
        "Export Center",
        "Download decision-ready artifacts for analysis, documentation, or an executive summary.",
    )
    summary_md = executive_summary_markdown(kpis, recommendations, scenario_result)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Filtered dataset CSV", dataframe_to_csv_bytes(filtered_data), "decision_lab_filtered_data.csv", "text/csv")
        st.download_button("KPI summary CSV", dataframe_to_csv_bytes(kpi_summary_frame(kpis)), "decision_lab_kpis.csv", "text/csv")
        st.download_button(
            "Recommendation summary CSV",
            dataframe_to_csv_bytes(recommendations_frame(recommendations)),
            "decision_lab_recommendations.csv",
            "text/csv",
        )
    with col2:
        st.download_button("Scenario result CSV", dataframe_to_csv_bytes(scenario_frame(scenario_result)), "decision_lab_scenario.csv", "text/csv")
        st.download_button("Executive summary Markdown", markdown_to_bytes(summary_md), "decision_lab_executive_summary.md", "text/markdown")
    st.markdown("### Executive summary preview")
    st.markdown(summary_md)


def render_methodology() -> None:
    render_section_header(
        "Methodology / Assumptions",
        "The app is intentionally transparent so the business logic can be explained in interviews.",
    )
    st.markdown(
        """
### Synthetic dataset
- The data is generated by `scripts/generate_sample_data.py`.
- It covers 36 months, 4 regions, 4 product categories, and 3 customer segments.
- It includes seasonality, regional demand/cost differences, segment economics, and retention risk.

### KPI definitions
- Revenue = units sold x average price.
- Gross margin = revenue x gross margin rate.
- Profit = gross margin - operating cost - marketing spend.
- Marketing efficiency = revenue / marketing spend.
- Retention and churn are weighted by units sold.

### Forecast method
- The forecast blends a linear monthly revenue trend with a recent moving average.
- The uncertainty band is based on historical residual variation.
- Forecasts are directional planning estimates, not guaranteed predictions.

### Scenario logic
- Marketing spend can lift demand using a simple elasticity assumption.
- Price increases can reduce demand.
- Cost changes affect cost of goods and operating cost.
- Retention changes lightly affect demand through customer health.

### Recommendation rules
- Recommendations are rule-based, prioritized, and tied to visible metrics.
- Rules check profitability, margin, growth trend, retention, region performance, product mix, and scenario risk.
- Every recommendation includes evidence and a suggested action.
        """
    )


def render_about(data: pd.DataFrame) -> None:
    render_section_header(
        "About This Project",
        "Portfolio positioning for GitHub, LinkedIn, and analytics internship applications.",
    )
    render_callout("Project summary", APP_SUMMARY)
    st.markdown(
        f"""
### Why this project exists
Retail KPI & Forecasting Sandbox demonstrates a complete analytics workflow: generate realistic demo data, store it in SQLite, calculate KPIs, forecast revenue, run scenarios, and translate metrics into executive recommendations.

### What it demonstrates
- Python analytics engineering with pandas and SQLite.
- Streamlit product UI design.
- Plotly dashboard visualization.
- Explainable forecasting and scenario modeling.
- Rule-based recommendation logic.
- Documentation and media workflow for public validation.

### Current dataset
- Records: {len(data):,}
- Date range: {data['month'].min().date()} to {data['month'].max().date()}
- Public-safe modeled retail data only.
        """
    )


def main() -> None:
    data = get_data()
    section_label, filtered_data = _render_sidebar(data)
    date_min = str(data["month"].min().date())
    date_max = str(data["month"].max().date())
    render_hero(len(data), date_min, date_max)

    if filtered_data.empty:
        render_empty_state("No records match the current filters. Adjust the sidebar controls.")
        return

    kpis = calculate_kpis(filtered_data)
    trends = monthly_trends(filtered_data)
    scenario_result = run_scenario(kpis, **DEFAULT_SCENARIO)
    recommendations = generate_recommendations(filtered_data, kpis, scenario_result)

    if section_label == "Executive Overview":
        render_executive_overview(filtered_data, kpis, trends)
    elif section_label == "KPI Explorer":
        render_kpi_explorer(filtered_data, kpis, trends)
    elif section_label == "Revenue & Profit Trends":
        render_trends(filtered_data, trends)
    elif section_label == "Forecasting Lab":
        render_forecasting_lab(filtered_data)
    elif section_label == "Scenario Analysis":
        scenario_result = render_scenario_analysis(kpis)
    elif section_label == "Executive Recommendations":
        recommendations = render_recommendations(filtered_data, kpis, scenario_result)
    elif section_label == "Data Explorer":
        render_data_explorer(filtered_data)
    elif section_label == "Export Center":
        render_export_center(filtered_data, kpis, recommendations, scenario_result)
    elif section_label == "Methodology / Assumptions":
        render_methodology()
    elif section_label == "About This Project":
        render_about(data)


if __name__ == "__main__":
    main()
