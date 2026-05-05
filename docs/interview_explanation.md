# Interview Explanation

## Short Pitch

Retail KPI & Forecasting Sandbox is a Streamlit analytics workflow that turns modeled retail operating data into KPIs, forecasts, scenario analysis, and executive recommendations. I built it to show that I can move beyond charting and create a tool that helps a business user decide what to do next.

## Why I Built It

Many dashboards stop at reporting. They show revenue, cost, and margin but do not clearly explain the decision implications. I wanted this project to demonstrate the full workflow from data generation and storage to decision support and executive communication.

## Problem It Solves

The app helps answer:

- Which region or product category is strongest?
- Is profit improving or weakening?
- Are costs rising faster than revenue?
- What happens if marketing spend, prices, costs, demand, or retention changes?
- What recommendation should leadership consider next?

## Technologies Used

- Python for analytics logic.
- pandas and NumPy for data manipulation and forecasting math.
- SQLite for local data storage.
- Streamlit for the dashboard interface.
- Plotly for charts.
- Playwright for validation screenshots and demo video.
- pytest for testing business logic.

## How It Works

The project starts with a deterministic retail operating data generator. The data is saved as CSV and loaded into SQLite. The dashboard loads filtered data and passes it into separate modules:

- KPI engine for revenue, profit, margin, costs, retention, and trend calculations.
- Forecasting engine for a transparent revenue forecast.
- Scenario engine for business assumption modeling.
- Recommendation engine for rule-based executive recommendations.
- Export module for CSV and Markdown summaries.

## Business Value

The app connects metrics to decisions. A user does not have to interpret every chart manually. The dashboard highlights strengths, risks, opportunities, and recommended actions with metric-based evidence.

## What I Would Improve Next

- Add validated user CSV uploads.
- Add product-level scenario elasticity.
- Add HTML or PDF executive reports.
- Add anomaly detection for margin, cost, and retention shifts.
- Add optional deployment or Docker packaging.

## Forecast Explanation

The forecast blends a linear trend with a recent moving average. I chose that method because the goal is explainable business planning, not a black-box machine learning demo. The app clearly says forecasts are directional and not guaranteed predictions.

## Recommendation Explanation

The recommendations are rule-based. Each recommendation has a priority, evidence, and suggested action tied to visible metrics such as profit margin, revenue trend, churn risk, product mix, regional performance, or scenario risk.
