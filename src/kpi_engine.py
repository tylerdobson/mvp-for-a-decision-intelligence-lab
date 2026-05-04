"""KPI calculation engine for business decision analysis."""

from __future__ import annotations

import pandas as pd

from src.utils import pct_change, safe_divide


NUMERIC_COLUMNS = [
    "marketing_spend",
    "operating_cost",
    "units_sold",
    "average_price",
    "revenue",
    "gross_margin",
    "profit",
    "retention_rate",
    "churn_risk",
]


def _empty_kpis() -> dict[str, float | str]:
    return {
        "revenue": 0.0,
        "profit": 0.0,
        "gross_margin": 0.0,
        "gross_margin_rate": 0.0,
        "profit_margin": 0.0,
        "operating_cost": 0.0,
        "marketing_spend": 0.0,
        "units_sold": 0.0,
        "average_price": 0.0,
        "retention_rate": 0.0,
        "churn_risk": 0.0,
        "marketing_efficiency": 0.0,
        "revenue_mom_pct": 0.0,
        "profit_mom_pct": 0.0,
        "best_region": "N/A",
        "worst_region": "N/A",
        "best_category": "N/A",
        "worst_category": "N/A",
    }


def calculate_kpis(df: pd.DataFrame) -> dict[str, float | str]:
    """Calculate executive KPIs from the filtered business dataset."""

    if df.empty:
        return _empty_kpis()

    data = df.copy()
    data["month"] = pd.to_datetime(data["month"])

    revenue = float(data["revenue"].sum())
    profit = float(data["profit"].sum())
    gross_margin = float(data["gross_margin"].sum())
    operating_cost = float(data["operating_cost"].sum())
    marketing_spend = float(data["marketing_spend"].sum())
    units_sold = float(data["units_sold"].sum())

    monthly = (
        data.groupby("month", as_index=False)
        .agg({"revenue": "sum", "profit": "sum"})
        .sort_values("month")
    )
    if len(monthly) >= 2:
        current = monthly.iloc[-1]
        previous = monthly.iloc[-2]
        revenue_mom_pct = pct_change(float(current["revenue"]), float(previous["revenue"]))
        profit_mom_pct = pct_change(float(current["profit"]), float(previous["profit"]))
    else:
        revenue_mom_pct = 0.0
        profit_mom_pct = 0.0

    region_performance = performance_by_dimension(data, "region")
    category_performance = performance_by_dimension(data, "product_category")

    return {
        "revenue": revenue,
        "profit": profit,
        "gross_margin": gross_margin,
        "gross_margin_rate": safe_divide(gross_margin, revenue),
        "profit_margin": safe_divide(profit, revenue),
        "operating_cost": operating_cost,
        "marketing_spend": marketing_spend,
        "units_sold": units_sold,
        "average_price": safe_divide(revenue, units_sold),
        "retention_rate": _weighted_average(data, "retention_rate", "units_sold"),
        "churn_risk": _weighted_average(data, "churn_risk", "units_sold"),
        "marketing_efficiency": safe_divide(revenue, marketing_spend),
        "revenue_mom_pct": revenue_mom_pct,
        "profit_mom_pct": profit_mom_pct,
        "best_region": _best_label(region_performance),
        "worst_region": _worst_label(region_performance),
        "best_category": _best_label(category_performance),
        "worst_category": _worst_label(category_performance),
    }


def monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate monthly KPI trends for charts and forecasting."""

    columns = [
        "month",
        "revenue",
        "gross_margin",
        "profit",
        "operating_cost",
        "marketing_spend",
        "units_sold",
        "gross_margin_rate",
        "profit_margin",
        "revenue_mom_pct",
        "profit_mom_pct",
    ]
    if df.empty:
        return pd.DataFrame(columns=columns)

    data = df.copy()
    data["month"] = pd.to_datetime(data["month"])
    monthly = (
        data.groupby("month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            gross_margin=("gross_margin", "sum"),
            profit=("profit", "sum"),
            operating_cost=("operating_cost", "sum"),
            marketing_spend=("marketing_spend", "sum"),
            units_sold=("units_sold", "sum"),
        )
        .sort_values("month")
    )
    monthly["gross_margin_rate"] = monthly["gross_margin"] / monthly["revenue"]
    monthly["profit_margin"] = monthly["profit"] / monthly["revenue"]
    monthly["revenue_mom_pct"] = monthly["revenue"].pct_change().fillna(0) * 100
    monthly["profit_mom_pct"] = monthly["profit"].pct_change().fillna(0) * 100
    return monthly[columns]


def performance_by_dimension(
    df: pd.DataFrame,
    dimension: str,
    sort_by: str = "profit",
) -> pd.DataFrame:
    """Aggregate performance by a categorical dimension."""

    if df.empty:
        return pd.DataFrame(
            columns=[
                dimension,
                "revenue",
                "gross_margin",
                "profit",
                "operating_cost",
                "marketing_spend",
                "units_sold",
                "gross_margin_rate",
                "profit_margin",
                "marketing_efficiency",
            ]
        )

    grouped = (
        df.groupby(dimension, as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            gross_margin=("gross_margin", "sum"),
            profit=("profit", "sum"),
            operating_cost=("operating_cost", "sum"),
            marketing_spend=("marketing_spend", "sum"),
            units_sold=("units_sold", "sum"),
        )
        .sort_values(sort_by, ascending=False)
    )
    grouped["gross_margin_rate"] = grouped["gross_margin"] / grouped["revenue"]
    grouped["profit_margin"] = grouped["profit"] / grouped["revenue"]
    grouped["marketing_efficiency"] = grouped["revenue"] / grouped["marketing_spend"]
    return grouped.reset_index(drop=True)


def _weighted_average(df: pd.DataFrame, value_column: str, weight_column: str) -> float:
    total_weight = float(df[weight_column].sum())
    if total_weight == 0:
        return 0.0
    return float((df[value_column] * df[weight_column]).sum() / total_weight)


def _best_label(performance: pd.DataFrame) -> str:
    if performance.empty:
        return "N/A"
    return str(performance.iloc[0, 0])


def _worst_label(performance: pd.DataFrame) -> str:
    if performance.empty:
        return "N/A"
    return str(performance.iloc[-1, 0])
