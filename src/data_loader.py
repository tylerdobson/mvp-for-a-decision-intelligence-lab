"""Data loading and filtering helpers for the Streamlit app."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.database import DEFAULT_DB_PATH, ensure_database, query_dataframe


BASE_QUERY = """
SELECT
    month,
    region,
    product_category,
    customer_segment,
    marketing_spend,
    operating_cost,
    units_sold,
    average_price,
    revenue,
    gross_margin_rate,
    gross_margin,
    profit,
    retention_rate,
    churn_risk
FROM business_metrics
ORDER BY month, region, product_category, customer_segment;
"""


def load_business_data(db_path: Path | str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Load the full business dataset from SQLite."""

    db_path = ensure_database(db_path)
    df = query_dataframe(BASE_QUERY, db_path=db_path)
    df["month"] = pd.to_datetime(df["month"])
    return df


def get_filter_options(df: pd.DataFrame) -> dict[str, list[str] | date]:
    """Return unique filter values for the dashboard sidebar."""

    return {
        "regions": sorted(df["region"].dropna().unique().tolist()),
        "product_categories": sorted(df["product_category"].dropna().unique().tolist()),
        "customer_segments": sorted(df["customer_segment"].dropna().unique().tolist()),
        "min_date": df["month"].min().date(),
        "max_date": df["month"].max().date(),
    }


def filter_business_data(
    df: pd.DataFrame,
    regions: list[str] | None = None,
    product_categories: list[str] | None = None,
    customer_segments: list[str] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Apply dashboard filters to the business dataset."""

    filtered = df.copy()

    if regions:
        filtered = filtered[filtered["region"].isin(regions)]
    if product_categories:
        filtered = filtered[filtered["product_category"].isin(product_categories)]
    if customer_segments:
        filtered = filtered[filtered["customer_segment"].isin(customer_segments)]
    if start_date:
        filtered = filtered[filtered["month"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["month"] <= pd.to_datetime(end_date)]

    return filtered.reset_index(drop=True)
