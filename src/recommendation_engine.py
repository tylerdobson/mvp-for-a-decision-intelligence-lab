"""Rule-based executive recommendation engine."""

from __future__ import annotations

import pandas as pd

from src.kpi_engine import calculate_kpis, performance_by_dimension
from src.utils import format_currency, format_delta_pct, format_percentage


PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def generate_recommendations(
    df: pd.DataFrame,
    kpis: dict[str, float | str] | None = None,
    scenario_result: dict[str, float | str] | None = None,
) -> list[dict[str, str]]:
    """Generate explainable recommendations tied to KPI evidence."""

    kpis = kpis or calculate_kpis(df)
    recommendations: list[dict[str, str]] = []

    if df.empty:
        return [
            _build_recommendation(
                "High",
                "Data coverage",
                "Widen the filter selection before making a decision.",
                "The current filter selection has no records, so KPI and scenario outputs are not decision-ready.",
                "Reset one or more filters and confirm the dataset contains enough months for trend analysis.",
            )
        ]

    _profitability_rules(recommendations, kpis)
    _growth_rules(recommendations, kpis)
    _retention_rules(recommendations, kpis)
    _region_rules(recommendations, df, kpis)
    _category_rules(recommendations, df, kpis)
    _scenario_rules(recommendations, scenario_result)
    _strength_rules(recommendations, kpis)

    if not recommendations:
        recommendations.append(
            _build_recommendation(
                "Low",
                "Operating plan",
                "Maintain the current strategy and monitor monthly trend changes.",
                "Revenue, profit, margin, and retention are within acceptable ranges for the selected data.",
                "Review this view monthly and rerun scenarios before changing spend, pricing, or cost plans.",
            )
        )

    recommendations.sort(key=lambda rec: PRIORITY_ORDER.get(rec["priority"], 99))
    return recommendations[:8]


def _build_recommendation(
    priority: str,
    theme: str,
    recommendation: str,
    evidence: str,
    action: str,
) -> dict[str, str]:
    """Create a recommendation record with backward-compatible reason text."""

    return {
        "priority": priority,
        "theme": theme,
        "recommendation": recommendation,
        "evidence": evidence,
        "action": action,
        "reason": evidence,
    }


def _add_recommendation(
    recommendations: list[dict[str, str]],
    priority: str,
    theme: str,
    recommendation: str,
    evidence: str,
    action: str,
) -> None:
    recommendations.append(_build_recommendation(priority, theme, recommendation, evidence, action))


def _profitability_rules(recommendations: list[dict[str, str]], kpis: dict[str, float | str]) -> None:
    gross_margin_rate = float(kpis["gross_margin_rate"])
    profit_margin = float(kpis["profit_margin"])
    operating_cost = float(kpis["operating_cost"])
    revenue = float(kpis["revenue"])

    if profit_margin < 0.08:
        _add_recommendation(
            recommendations,
            "High",
            "Profitability",
            "Reduce cost pressure before scaling growth programs.",
            (
                f"Profit margin is {format_percentage(profit_margin)}, below the 8% risk threshold. "
                f"Operating cost is {format_currency(operating_cost)} against revenue of {format_currency(revenue)}."
            ),
            "Audit discounting, fulfillment costs, and fixed operating expenses before adding more demand-generation spend.",
        )
    elif gross_margin_rate < 0.30:
        _add_recommendation(
            recommendations,
            "Medium",
            "Margin",
            "Review pricing and product mix for low-margin sales.",
            f"Gross margin is {format_percentage(gross_margin_rate)}, below the 30% target used by this app.",
            "Compare low-margin categories against volume contribution and decide whether to reprice, bundle, or reduce cost.",
        )


def _growth_rules(recommendations: list[dict[str, str]], kpis: dict[str, float | str]) -> None:
    revenue_mom_pct = float(kpis["revenue_mom_pct"])
    profit_mom_pct = float(kpis["profit_mom_pct"])

    if revenue_mom_pct <= -5:
        _add_recommendation(
            recommendations,
            "High",
            "Revenue trend",
            "Investigate the latest monthly revenue decline before increasing spend.",
            f"Revenue changed {revenue_mom_pct:.1f}% month over month in the selected data.",
            "Identify whether the decline came from demand, price, segment mix, or one region before changing budget allocation.",
        )
    if profit_mom_pct < revenue_mom_pct - 5:
        _add_recommendation(
            recommendations,
            "High",
            "Cost control",
            "Monitor operating costs because profit is falling faster than revenue.",
            (
                f"Profit changed {profit_mom_pct:.1f}% month over month while revenue changed "
                f"{revenue_mom_pct:.1f}%."
            ),
            "Review operating-cost categories and pause broad growth initiatives until profit trend stabilizes.",
        )


def _retention_rules(recommendations: list[dict[str, str]], kpis: dict[str, float | str]) -> None:
    retention_rate = float(kpis["retention_rate"])
    churn_risk = float(kpis["churn_risk"])

    if retention_rate < 0.82 or churn_risk > 0.18:
        _add_recommendation(
            recommendations,
            "High",
            "Retention",
            "Prioritize retention actions before aggressive acquisition spend.",
            (
                f"Weighted retention is {format_percentage(retention_rate)} and churn risk is "
                f"{format_percentage(churn_risk)}."
            ),
            "Focus on onboarding, customer success outreach, and renewal-risk segments before increasing acquisition spend.",
        )


def _region_rules(recommendations: list[dict[str, str]], df: pd.DataFrame, kpis: dict[str, float | str]) -> None:
    region_perf = performance_by_dimension(df, "region")
    if region_perf.empty:
        return

    overall_margin = float(kpis["gross_margin_rate"])
    overall_efficiency = float(kpis["marketing_efficiency"])
    top_region = region_perf.iloc[0]
    weakest_region = region_perf.iloc[-1]
    top_margin = float(top_region["gross_margin_rate"])
    top_efficiency = float(top_region["marketing_efficiency"])
    weakest_profit_margin = float(weakest_region["profit_margin"])

    if top_margin >= overall_margin + 0.03 and top_efficiency >= overall_efficiency:
        _add_recommendation(
            recommendations,
            "Medium",
            "Regional growth",
            f"Increase focus on the {top_region['region']} region.",
            (
                f"{top_region['region']} leads profit contribution with {format_percentage(top_margin)} gross margin "
                f"and {top_efficiency:.1f}x revenue per marketing dollar."
            ),
            "Pilot incremental marketing spend in this region and compare marginal profit against the portfolio average.",
        )

    if weakest_profit_margin < 0.10:
        _add_recommendation(
            recommendations,
            "Medium",
            "Regional risk",
            f"Investigate margin pressure in the {weakest_region['region']} region.",
            (
                f"{weakest_region['region']} has {format_percentage(weakest_profit_margin)} profit margin, "
                f"below the portfolio profit margin of {format_percentage(float(kpis['profit_margin']))}."
            ),
            "Review product mix, discounting, and operating cost before expanding spend in this region.",
        )


def _category_rules(recommendations: list[dict[str, str]], df: pd.DataFrame, kpis: dict[str, float | str]) -> None:
    category_perf = performance_by_dimension(df, "product_category")
    if category_perf.empty:
        return

    overall_margin = float(kpis["gross_margin_rate"])
    total_units = float(category_perf["units_sold"].sum())
    if total_units == 0:
        return

    category_perf = category_perf.copy()
    category_perf["unit_share"] = category_perf["units_sold"] / total_units
    risky_categories = category_perf[
        (category_perf["gross_margin_rate"] < overall_margin - 0.05)
        & (category_perf["unit_share"] >= 0.20)
    ]

    if not risky_categories.empty:
        category = risky_categories.sort_values("unit_share", ascending=False).iloc[0]
        _add_recommendation(
            recommendations,
            "Medium",
            "Product mix",
            f"Improve economics for {category['product_category']} before pushing more volume.",
            (
                f"{category['product_category']} represents {category['unit_share'] * 100:.1f}% of units "
                f"but only has {format_percentage(float(category['gross_margin_rate']))} gross margin."
            ),
            "Review pricing, delivery cost, and packaging before using this category as a growth lever.",
        )


def _scenario_rules(recommendations: list[dict[str, str]], scenario_result: dict[str, float | str] | None) -> None:
    if not scenario_result:
        return

    risk_level = str(scenario_result["risk_level"])
    profit_delta_pct = float(scenario_result["profit_delta_pct"])
    revenue_delta_pct = float(scenario_result.get("revenue_delta_pct", 0.0))

    if risk_level == "High":
        _add_recommendation(
            recommendations,
            "High",
            "Scenario risk",
            "Revise the scenario before making an executive decision.",
            (
                f"The current assumptions create a High risk scenario with estimated profit change of "
                f"{format_delta_pct(profit_delta_pct)}."
            ),
            "Reduce the most aggressive assumption and rerun the scenario before recommending rollout.",
        )
    elif profit_delta_pct >= 5:
        _add_recommendation(
            recommendations,
            "Medium",
            "Scenario opportunity",
            "Pilot the selected scenario in a limited market.",
            (
                f"The scenario estimates {format_delta_pct(profit_delta_pct)} profit change and "
                f"{format_delta_pct(revenue_delta_pct)} revenue change with {risk_level} risk."
            ),
            "Run a time-boxed pilot in one region or category and compare actual lift to the model.",
        )


def _strength_rules(recommendations: list[dict[str, str]], kpis: dict[str, float | str]) -> None:
    if float(kpis["profit_margin"]) >= 0.16 and float(kpis["revenue_mom_pct"]) > 0:
        _add_recommendation(
            recommendations,
            "Low",
            "Strength to protect",
            "Protect the current profitable growth pattern while testing targeted upside.",
            (
                f"Profit margin is {format_percentage(float(kpis['profit_margin']))} and revenue moved "
                f"{format_delta_pct(float(kpis['revenue_mom_pct']))} month over month."
            ),
            "Use scenario analysis to test small budget or pricing changes without disrupting the current margin profile.",
        )
