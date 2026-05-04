"""Scenario analysis engine for estimating business impact."""

from __future__ import annotations

from src.utils import pct_change, safe_divide


DEFAULT_ASSUMPTIONS = {
    "marketing_elasticity": 0.25,
    "price_elasticity": -0.35,
    "minimum_demand_multiplier": 0.15,
}


def run_scenario(
    baseline_metrics: dict[str, float],
    marketing_change_pct: float = 0.0,
    price_change_pct: float = 0.0,
    cost_change_pct: float = 0.0,
    demand_change_pct: float = 0.0,
    assumptions: dict[str, float] | None = None,
) -> dict[str, float | str]:
    """Estimate financial impact from user-controlled scenario assumptions.

    Inputs are percentage values. For example, pass 10 for a 10 percent increase.
    """

    assumptions = {**DEFAULT_ASSUMPTIONS, **(assumptions or {})}
    marketing_change = marketing_change_pct / 100
    price_change = price_change_pct / 100
    cost_change = cost_change_pct / 100
    demand_change = demand_change_pct / 100

    baseline_revenue = float(baseline_metrics.get("revenue", 0.0))
    baseline_profit = float(baseline_metrics.get("profit", 0.0))
    baseline_gross_margin = float(baseline_metrics.get("gross_margin", 0.0))
    baseline_operating_cost = float(baseline_metrics.get("operating_cost", 0.0))
    baseline_marketing_spend = float(baseline_metrics.get("marketing_spend", 0.0))
    baseline_units = float(baseline_metrics.get("units_sold", 0.0))
    baseline_average_price = float(baseline_metrics.get("average_price", 0.0))

    demand_multiplier = (
        1
        + demand_change
        + (marketing_change * assumptions["marketing_elasticity"])
        + (price_change * assumptions["price_elasticity"])
    )
    demand_multiplier = max(
        demand_multiplier,
        assumptions["minimum_demand_multiplier"],
    )

    adjusted_units = baseline_units * demand_multiplier
    adjusted_price = baseline_average_price * (1 + price_change)
    adjusted_revenue = adjusted_units * adjusted_price

    baseline_cogs = max(baseline_revenue - baseline_gross_margin, 0.0)
    adjusted_cogs = baseline_cogs * demand_multiplier * (1 + cost_change)
    adjusted_gross_margin = adjusted_revenue - adjusted_cogs
    adjusted_operating_cost = baseline_operating_cost * (1 + cost_change)
    adjusted_marketing_spend = baseline_marketing_spend * (1 + marketing_change)
    adjusted_profit = (
        adjusted_gross_margin - adjusted_operating_cost - adjusted_marketing_spend
    )

    adjusted_gross_margin_rate = safe_divide(adjusted_gross_margin, adjusted_revenue)
    adjusted_profit_margin = safe_divide(adjusted_profit, adjusted_revenue)

    result = {
        "adjusted_revenue": adjusted_revenue,
        "adjusted_profit": adjusted_profit,
        "adjusted_gross_margin": adjusted_gross_margin,
        "adjusted_gross_margin_rate": adjusted_gross_margin_rate,
        "adjusted_profit_margin": adjusted_profit_margin,
        "adjusted_units_sold": adjusted_units,
        "adjusted_marketing_spend": adjusted_marketing_spend,
        "adjusted_operating_cost": adjusted_operating_cost,
        "revenue_delta": adjusted_revenue - baseline_revenue,
        "profit_delta": adjusted_profit - baseline_profit,
        "gross_margin_delta": adjusted_gross_margin - baseline_gross_margin,
        "revenue_delta_pct": pct_change(adjusted_revenue, baseline_revenue),
        "profit_delta_pct": pct_change(adjusted_profit, baseline_profit),
        "gross_margin_delta_pct": pct_change(
            adjusted_gross_margin,
            baseline_gross_margin,
        ),
        "demand_multiplier": demand_multiplier,
    }
    result["risk_level"] = classify_scenario_risk(
        result,
        max(
            abs(marketing_change_pct),
            abs(price_change_pct),
            abs(cost_change_pct),
            abs(demand_change_pct),
        ),
    )
    result["recommended_action"] = recommend_scenario_action(result)
    return result


def classify_scenario_risk(
    scenario_result: dict[str, float | str],
    max_assumption_change_pct: float,
) -> str:
    """Classify the business risk of a scenario."""

    profit_delta_pct = float(scenario_result["profit_delta_pct"])
    profit_margin = float(scenario_result["adjusted_profit_margin"])
    gross_margin_rate = float(scenario_result["adjusted_gross_margin_rate"])
    adjusted_profit = float(scenario_result["adjusted_profit"])

    if (
        adjusted_profit < 0
        or profit_delta_pct <= -10
        or profit_margin < 0.08
        or max_assumption_change_pct >= 35
    ):
        return "High"
    if profit_delta_pct < 0 or gross_margin_rate < 0.28 or max_assumption_change_pct >= 20:
        return "Medium"
    return "Low"


def recommend_scenario_action(scenario_result: dict[str, float | str]) -> str:
    """Turn scenario output into a concise recommended action."""

    revenue_delta_pct = float(scenario_result["revenue_delta_pct"])
    profit_delta_pct = float(scenario_result["profit_delta_pct"])
    risk_level = str(scenario_result["risk_level"])

    if risk_level == "High":
        return (
            "Do not roll this out broadly yet. Revise the assumptions, protect margin, "
            "and test in one region or category first."
        )
    if revenue_delta_pct > 0 and profit_delta_pct < 0:
        return (
            "Avoid scaling this scenario as designed. It grows revenue but weakens "
            "profit, so the economics need pricing or cost changes."
        )
    if profit_delta_pct >= 5 and risk_level in {"Low", "Medium"}:
        return (
            "Proceed with a controlled pilot. The scenario improves profit enough to "
            "justify testing before a full rollout."
        )
    if profit_delta_pct >= 0:
        return (
            "Consider a small pilot. The upside is modest, so validate customer demand "
            "before committing major resources."
        )
    return (
        "Hold the current plan. The scenario does not improve profit enough to justify "
        "the operational risk."
    )
