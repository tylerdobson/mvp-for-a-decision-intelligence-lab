"""Simple, explainable revenue forecasting."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.kpi_engine import monthly_trends
from src.utils import pct_change


def forecast_revenue(df: pd.DataFrame, periods: int = 6, window: int = 3) -> pd.DataFrame:
    """Forecast monthly revenue using a transparent trend and moving-average blend.

    This is intentionally simple for review clarity. It is not a financial
    prediction model and should be treated as directional decision support.
    """

    history = monthly_trends(df)[["month", "revenue"]].copy()
    if history.empty:
        return pd.DataFrame(
            columns=["month", "revenue", "lower_bound", "upper_bound", "series"]
        )

    history = history.sort_values("month").reset_index(drop=True)
    x = np.arange(len(history), dtype=float)
    y = history["revenue"].astype(float).to_numpy()

    if len(history) >= 2:
        slope, intercept = np.polyfit(x, y, deg=1)
        fitted = intercept + slope * x
        residuals = y - fitted
    else:
        slope = 0.0
        intercept = y[-1]
        residuals = np.array([0.0])

    recent_values = list(y[-window:])
    residual_std = float(np.std(residuals)) if len(residuals) > 1 else 0.0
    uncertainty_pct = min(max(residual_std / max(float(np.mean(y)), 1.0), 0.05), 0.22)

    forecast_rows = []
    last_month = history["month"].max()
    for step in range(1, periods + 1):
        trend_prediction = intercept + slope * (len(history) + step - 1)
        moving_average = float(np.mean(recent_values[-window:]))
        blended_prediction = (0.6 * trend_prediction) + (0.4 * moving_average)
        blended_prediction = max(blended_prediction, 0.0)

        forecast_month = last_month + pd.DateOffset(months=step)
        lower_bound = blended_prediction * (1 - uncertainty_pct)
        upper_bound = blended_prediction * (1 + uncertainty_pct)
        forecast_rows.append(
            {
                "month": forecast_month,
                "revenue": blended_prediction,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "series": "Forecast",
            }
        )
        recent_values.append(blended_prediction)

    history_rows = history.assign(
        lower_bound=np.nan,
        upper_bound=np.nan,
        series="Historical",
    )
    forecast = pd.DataFrame(forecast_rows)
    return pd.concat([history_rows, forecast], ignore_index=True)


def forecast_summary(forecast_df: pd.DataFrame) -> str:
    """Create a plain-English forecast explanation for the dashboard."""

    if forecast_df.empty or "Forecast" not in set(forecast_df["series"]):
        return "Not enough data is available to create a forecast."

    historical = forecast_df[forecast_df["series"] == "Historical"]
    forecast = forecast_df[forecast_df["series"] == "Forecast"]
    last_actual = float(historical["revenue"].iloc[-1])
    final_forecast = float(forecast["revenue"].iloc[-1])
    change_pct = pct_change(final_forecast, last_actual)
    direction = "higher" if change_pct >= 0 else "lower"

    return (
        f"The directional forecast estimates revenue will be {abs(change_pct):.1f}% "
        f"{direction} than the latest actual month by the end of the forecast window. "
        "This uses a blended linear trend and recent moving average, so it should be "
        "treated as planning guidance rather than a guaranteed prediction."
    )
