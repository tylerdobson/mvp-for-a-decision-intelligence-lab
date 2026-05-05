"""Generate deterministic sample retail operating data for Retail KPI & Forecasting Sandbox."""

from __future__ import annotations

import math
import random
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "sample_business_data.csv"
RANDOM_SEED = 42


REGIONS = {
    "Northeast": {"demand": 1.08, "cost": 1.08, "retention": 0.88},
    "Midwest": {"demand": 0.94, "cost": 0.92, "retention": 0.84},
    "South": {"demand": 1.14, "cost": 0.96, "retention": 0.81},
    "West": {"demand": 1.03, "cost": 1.12, "retention": 0.86},
}

PRODUCT_CATEGORIES = {
    "Analytics Software": {"base_units": 118, "price": 420, "margin": 0.58},
    "Implementation Services": {"base_units": 72, "price": 760, "margin": 0.42},
    "Training Workshops": {"base_units": 96, "price": 280, "margin": 0.48},
    "Support Plans": {"base_units": 138, "price": 190, "margin": 0.52},
}

CUSTOMER_SEGMENTS = {
    "Small Business": {"demand": 1.20, "price": 0.92, "margin": -0.02},
    "Mid-Market": {"demand": 1.00, "price": 1.00, "margin": 0.00},
    "Enterprise": {"demand": 0.72, "price": 1.22, "margin": 0.05},
}


def generate_sample_data(output_path: Path = OUTPUT_PATH) -> pd.DataFrame:
    """Create a realistic monthly business dataset and write it to CSV."""

    random.seed(RANDOM_SEED)
    months = pd.date_range("2023-01-01", periods=36, freq="MS")
    rows: list[dict[str, float | int | str]] = []

    for month_index, month in enumerate(months):
        trend = 1 + (month_index * 0.011)
        seasonality = 1 + (0.09 * math.sin((month.month - 1) / 12 * 2 * math.pi))
        if month.month in {10, 11}:
            seasonality += 0.08
        if month.month in {1, 2}:
            seasonality -= 0.04

        for region, region_profile in REGIONS.items():
            for product_category, product_profile in PRODUCT_CATEGORIES.items():
                for customer_segment, segment_profile in CUSTOMER_SEGMENTS.items():
                    demand_noise = random.uniform(0.86, 1.16)
                    units = int(
                        product_profile["base_units"]
                        * region_profile["demand"]
                        * segment_profile["demand"]
                        * trend
                        * seasonality
                        * demand_noise
                    )

                    average_price = (
                        product_profile["price"]
                        * segment_profile["price"]
                        * random.uniform(0.97, 1.04)
                    )
                    revenue = units * average_price

                    gross_margin_rate = _clamp(
                        product_profile["margin"]
                        + segment_profile["margin"]
                        + random.uniform(-0.025, 0.025),
                        0.24,
                        0.64,
                    )
                    gross_margin = revenue * gross_margin_rate

                    marketing_rate = 0.075 + random.uniform(-0.012, 0.016)
                    marketing_spend = max(1_200, revenue * marketing_rate)

                    operating_cost = (
                        5_400 * region_profile["cost"]
                        + (units * average_price * 0.105 * region_profile["cost"])
                        + random.uniform(-850, 1_150)
                    )
                    profit = gross_margin - operating_cost - marketing_spend

                    retention_rate = _clamp(
                        region_profile["retention"]
                        + (segment_profile["margin"] * 0.35)
                        + random.uniform(-0.035, 0.035),
                        0.68,
                        0.95,
                    )
                    churn_risk = 1 - retention_rate

                    rows.append(
                        {
                            "month": month.strftime("%Y-%m-%d"),
                            "region": region,
                            "product_category": product_category,
                            "customer_segment": customer_segment,
                            "marketing_spend": round(marketing_spend, 2),
                            "operating_cost": round(operating_cost, 2),
                            "units_sold": units,
                            "average_price": round(average_price, 2),
                            "revenue": round(revenue, 2),
                            "gross_margin_rate": round(gross_margin_rate, 4),
                            "gross_margin": round(gross_margin, 2),
                            "profit": round(profit, 2),
                            "retention_rate": round(retention_rate, 4),
                            "churn_risk": round(churn_risk, 4),
                        }
                    )

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


if __name__ == "__main__":
    data = generate_sample_data()
    print(f"Generated {len(data):,} rows at {OUTPUT_PATH}")
