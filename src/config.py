"""Application configuration for Retail KPI & Forecasting Sandbox."""

from __future__ import annotations

from dataclasses import dataclass


APP_TITLE = "Retail KPI & Forecasting Sandbox"
APP_TAGLINE = "From metrics to decisions, not just charts."
APP_SUMMARY = (
    "A reusable Streamlit analytics workflow that turns modeled retail operating data "
    "into KPIs, forecasts, scenario analysis, and executive recommendations."
)

BRAND_COLORS = {
    "ink": "#17201b",
    "muted": "#66706b",
    "canvas": "#f5f1e8",
    "panel": "#fffaf0",
    "border": "#ded3bf",
    "green": "#0f6b5f",
    "blue": "#233d70",
    "orange": "#b85c2b",
    "gold": "#bd7b21",
    "red": "#a73d2a",
}

CHART_COLORS = [
    BRAND_COLORS["green"],
    BRAND_COLORS["blue"],
    BRAND_COLORS["orange"],
    BRAND_COLORS["gold"],
    "#6f7f6b",
]


@dataclass(frozen=True)
class Section:
    """Dashboard navigation metadata."""

    label: str
    slug: str
    caption: str


NAV_SECTIONS = [
    Section("Executive Overview", "executive-overview", "Top KPIs, insights, and next action."),
    Section("KPI Explorer", "kpi-explorer", "Filtered KPI cards and performance drivers."),
    Section("Revenue & Profit Trends", "trends", "Monthly revenue, profit, costs, margin, and units."),
    Section("Forecasting Lab", "forecasting-lab", "Directional 3 to 6 month revenue forecast."),
    Section("Scenario Analysis", "scenario-analysis", "Decision simulation for business assumptions."),
    Section("Executive Recommendations", "executive-recommendations", "Rule-based recommendations with evidence."),
    Section("Data Explorer", "data-explorer", "Filtered row-level retail operating data view."),
    Section("Export Center", "export-center", "Download data, KPIs, recommendations, and summary."),
    Section("Methodology / Assumptions", "methodology", "Methods, assumptions, definitions, and limitations."),
    Section("About This Project", "about", "Portfolio positioning and project overview."),
]

SECTION_BY_SLUG = {section.slug: section for section in NAV_SECTIONS}
SECTION_LABELS = [section.label for section in NAV_SECTIONS]

DEFAULT_SCENARIO = {
    "marketing_change_pct": 10,
    "price_change_pct": 0,
    "cost_change_pct": 0,
    "demand_change_pct": 5,
    "retention_change_pct": 0,
}

MEDIA_FILES = [
    "hero.png",
    "dashboard-overview.png",
    "kpi-explorer.png",
    "forecasting-lab.png",
    "scenario-analysis.png",
    "executive-recommendations.png",
    "data-explorer.png",
    "demo-poster.png",
    "linkedin-cover.png",
]
