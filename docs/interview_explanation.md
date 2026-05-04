# Interview Explanation

## Short Pitch

Decision Intelligence Lab is a Streamlit analytics app that turns business data into KPIs, forecasts, scenario analysis, and executive recommendations. I built it to show that I can create more than charts. I can build an end-to-end analytics tool that helps a business decide what to do next.

## Why I Built It

Many dashboards stop at reporting. They show revenue, cost, and margin, but they do not clearly explain what action a decision-maker should consider. I wanted this project to show the full analytics workflow:

- Create realistic sample data.
- Store it in a local database.
- Calculate business KPIs.
- Forecast future revenue directionally.
- Let users test scenarios.
- Translate the outputs into recommendations.

## Problem It Solves

The app helps a business user answer questions like:

- Which region or product category is strongest?
- Is profit improving or weakening?
- Are costs rising faster than revenue?
- What happens if marketing spend, prices, costs, or demand changes?
- What recommendation should leadership consider?

## Technologies Used

- Python for the analytics logic.
- pandas for data manipulation.
- SQLite for local database storage.
- Streamlit for the interactive dashboard.
- Plotly for charts.
- NumPy for simple forecasting math.
- pytest for testing business logic.

## How The App Works

The project starts with a deterministic sample data generator. The data is saved as a CSV, then loaded into a SQLite database. Streamlit queries the database and passes the filtered data into separate modules:

- The KPI engine calculates revenue, profit, margin, costs, retention, and month-over-month changes.
- The forecasting engine creates a simple revenue forecast using a blended trend and moving average.
- The scenario engine estimates how changes in price, cost, demand, and marketing spend affect revenue and profit.
- The recommendation engine applies clear rules to produce executive-style recommendations with priority levels.

## Business Value

The app creates value because it connects data to decisions. A user does not have to interpret every chart manually. The dashboard highlights strengths, risks, and recommended actions with metric-based reasons.

## What I Would Improve Next

If I continued building this project, I would add:

- CSV upload so users can analyze their own business data.
- Exportable executive summary reports.
- More advanced scenario assumptions by product category.
- Automated screenshot generation for the README.
- Optional deployment with a hosted Streamlit or container setup.

## How I Would Explain The Forecast

The forecast is intentionally simple. It blends a linear trend with a recent moving average. I chose that this is a business analytics portfolio project, not a black-box machine learning demo. The app explains that the forecast is directional and should be validated with real data before making major decisions.

## How I Would Explain The Recommendations

The recommendations are rule-based. That means each recommendation can be traced back to a visible metric, such as profit margin, revenue trend, retention rate, or scenario risk. This makes the output explainable for business users.
