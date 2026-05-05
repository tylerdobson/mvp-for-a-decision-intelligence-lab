"""Reusable Streamlit UI components for Retail KPI & Forecasting Sandbox."""

from __future__ import annotations

import html
from typing import Iterable

import streamlit as st

from src.config import APP_TAGLINE, APP_TITLE, BRAND_COLORS
from src.utils import format_currency, format_delta_pct, format_number, format_percentage


CUSTOM_CSS = f"""
<style>
    :root {{
        --dil-bg: {BRAND_COLORS['canvas']};
        --dil-ink: {BRAND_COLORS['ink']};
        --dil-muted: {BRAND_COLORS['muted']};
        --dil-panel: {BRAND_COLORS['panel']};
        --dil-border: {BRAND_COLORS['border']};
        --dil-accent: {BRAND_COLORS['green']};
        --dil-warn: {BRAND_COLORS['orange']};
        --dil-risk: {BRAND_COLORS['red']};
    }}

    .stApp {{
        background:
            radial-gradient(circle at top left, rgba(15, 107, 95, 0.12), transparent 33rem),
            radial-gradient(circle at top right, rgba(184, 92, 43, 0.10), transparent 29rem),
            linear-gradient(180deg, #f8f1e5 0%, #f5f1e8 45%, #eee6da 100%);
        color: var(--dil-ink);
    }}

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    #MainMenu,
    footer {{
        display: none;
    }}

    .block-container {{
        padding-top: 2.4rem;
        padding-bottom: 3rem;
        max-width: 1440px;
    }}

    h1, h2, h3 {{
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: -0.035em;
    }}

    [data-testid="stSidebar"] {{
        background: #efe6d7;
        border-right: 1px solid var(--dil-border);
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        letter-spacing: -0.02em;
    }}

    div[data-testid="stMetric"] {{
        background: rgba(255, 250, 240, 0.90);
        border: 1px solid var(--dil-border);
        border-radius: 20px;
        padding: 18px 18px 14px;
        box-shadow: 0 18px 42px rgba(52, 41, 27, 0.08);
    }}

    div[data-testid="stMetricLabel"] p {{
        color: var(--dil-muted);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }}

    .dil-hero {{
        position: relative;
        overflow: hidden;
        border: 1px solid var(--dil-border);
        border-radius: 30px;
        padding: 34px 38px;
        background:
            linear-gradient(135deg, rgba(255,250,240,0.97), rgba(226, 239, 229, 0.89)),
            repeating-linear-gradient(90deg, rgba(15,107,95,0.06) 0 1px, transparent 1px 52px);
        box-shadow: 0 26px 64px rgba(52, 41, 27, 0.12);
        margin-bottom: 20px;
    }}

    .dil-eyebrow {{
        color: var(--dil-accent);
        font-size: 0.78rem;
        font-weight: 900;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }}

    .dil-hero h1 {{
        margin: 0;
        font-size: clamp(2.4rem, 5vw, 4.8rem);
        line-height: 0.95;
    }}

    .dil-hero p {{
        color: var(--dil-muted);
        max-width: 920px;
        font-size: 1.08rem;
        line-height: 1.65;
        margin-top: 1rem;
    }}

    .dil-badge-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }}

    .dil-badge {{
        border: 1px solid rgba(15,107,95,0.24);
        background: rgba(255,255,255,0.48);
        color: var(--dil-ink);
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.82rem;
        font-weight: 700;
    }}

    .dil-card-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
        gap: 14px;
        margin: 12px 0 20px;
    }}

    .dil-card {{
        background: rgba(255, 250, 240, 0.88);
        border: 1px solid var(--dil-border);
        border-radius: 20px;
        padding: 18px 18px 16px;
        box-shadow: 0 18px 42px rgba(52, 41, 27, 0.07);
    }}

    .dil-card strong {{
        display: block;
        font-size: 0.98rem;
        margin-bottom: 8px;
    }}

    .dil-card p {{
        color: var(--dil-muted);
        margin: 0;
        line-height: 1.55;
    }}

    .dil-callout {{
        border-left: 5px solid var(--dil-accent);
        background: rgba(255,250,240,0.86);
        padding: 18px 20px;
        border-radius: 16px;
        margin: 12px 0 18px;
        box-shadow: 0 14px 32px rgba(52, 41, 27, 0.06);
    }}

    .priority-high {{ border-left-color: var(--dil-risk); }}
    .priority-medium {{ border-left-color: var(--dil-warn); }}
    .priority-low {{ border-left-color: var(--dil-accent); }}

    .dil-muted {{ color: var(--dil-muted); }}
    .dil-divider {{ height: 1px; background: var(--dil-border); margin: 18px 0; }}
</style>
"""


def apply_page_style() -> None:
    """Inject the app CSS."""

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero(record_count: int, date_min: str, date_max: str) -> None:
    """Render the dashboard landing hero."""

    st.markdown(
        (
            '<div class="dil-hero">'
            '<div class="dil-eyebrow">Decision support analytics product</div>'
            f"<h1>{APP_TITLE}</h1>"
            f"<p>{APP_TAGLINE} This dashboard turns operating data into KPIs, forecasts, "
            "scenario analysis, and explainable recommendations so a user can decide what to do next.</p>"
            '<div class="dil-badge-row">'
            f'<span class="dil-badge">{record_count:,} modeled records</span>'
            f'<span class="dil-badge">{html.escape(date_min)} to {html.escape(date_max)}</span>'
            '<span class="dil-badge">SQLite + Streamlit + Plotly</span>'
            '<span class="dil-badge">Rule-based recommendations</span>'
            "</div></div>"
        ),
        unsafe_allow_html=True,
    )


def render_section_header(title: str, caption: str) -> None:
    st.markdown(f"## {title}")
    st.caption(caption)


def render_metric_row(kpis: dict[str, float | str]) -> None:
    """Render headline KPI cards."""

    columns = st.columns(6)
    metrics = [
        ("Revenue", format_currency(float(kpis["revenue"])), format_delta_pct(float(kpis["revenue_mom_pct"]))),
        ("Profit", format_currency(float(kpis["profit"])), format_delta_pct(float(kpis["profit_mom_pct"]))),
        ("Gross Margin", format_percentage(float(kpis["gross_margin_rate"])), None),
        ("Operating Cost", format_currency(float(kpis["operating_cost"])), None),
        ("Units Sold", format_number(float(kpis["units_sold"])), None),
        ("Churn Risk", format_percentage(float(kpis["churn_risk"])), None),
    ]
    for column, (label, value, delta) in zip(columns, metrics):
        with column:
            st.metric(label=label, value=value, delta=delta)


def render_insight_cards(insights: Iterable[dict[str, str]]) -> None:
    cards = []
    for insight in insights:
        cards.append(
            '<div class="dil-card">'
            f"<strong>{html.escape(insight['title'])}</strong>"
            f"<p>{html.escape(insight['body'])}</p>"
            "</div>"
        )
    st.markdown(f"<div class='dil-card-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)


def render_recommendation_card(rec: dict[str, str]) -> None:
    priority = rec.get("priority", "Low")
    priority_class = priority.lower()
    recommendation = html.escape(rec.get("recommendation", "Review the current operating plan."))
    evidence = html.escape(rec.get("evidence", rec.get("reason", "No evidence supplied.")))
    action = html.escape(rec.get("action", "Monitor the metric and validate before changing the plan."))
    theme = html.escape(rec.get("theme", "Operating plan"))
    st.markdown(
        (
            f'<div class="dil-callout priority-{priority_class}">'
            f"<strong>{html.escape(priority)} Priority - {theme}</strong><br>"
            f"<b>Recommendation:</b> {recommendation}<br>"
            f'<b>Evidence:</b> <span class="dil-muted">{evidence}</span><br>'
            f'<b>Action:</b> <span class="dil-muted">{action}</span>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_callout(title: str, body: str) -> None:
    st.markdown(
        (
            '<div class="dil-callout">'
            f"<strong>{html.escape(title)}</strong><br>"
            f'<span class="dil-muted">{html.escape(body)}</span>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_empty_state(message: str) -> None:
    st.warning(message)
