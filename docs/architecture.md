# Architecture

Decision Intelligence Lab is designed as a small, understandable analytics system. The app separates data storage, business logic, and presentation so each layer can be tested and improved independently.

## High-Level Flow

```text
CSV sample data
  -> SQLite database
  -> data loader
  -> KPI, forecast, scenario, and recommendation engines
  -> Streamlit dashboard
```

## Components

### Streamlit App

`app.py` is the user interface. It loads data from SQLite, applies filters, calls the business logic modules, and displays charts, KPI cards, scenario outputs, and recommendations.

The app has five sections:

- Executive Overview
- KPI Explorer
- Forecasting
- Scenario Analysis
- Executive Recommendations

### SQLite Database

The local database lives at `database/decision_lab.db`. It stores the synthetic business dataset in one table called `business_metrics`.

`sql/create_tables.sql` defines the schema and indexes. `scripts/setup_database.py` rebuilds the database from the CSV file.

### Data Loader

`src/data_loader.py` owns dashboard data access and filter logic. It loads records from SQLite and returns pandas DataFrames for analysis.

### Database Utilities

`src/database.py` handles SQLite connections, schema creation, CSV loading, and query execution.

### KPI Engine

`src/kpi_engine.py` calculates the main metrics:

- Revenue
- Profit
- Gross margin
- Profit margin
- Operating cost
- Marketing spend
- Units sold
- Average price
- Retention rate
- Churn risk
- Month-over-month revenue and profit change
- Best and worst region/category

### Forecasting Engine

`src/forecasting.py` creates a simple revenue forecast. It blends:

- A linear trend across monthly revenue.
- A recent moving average.

This approach is intentionally transparent. It is suitable for explaining directional planning but should not be treated as a precise prediction model.

### Scenario Engine

`src/scenario_engine.py` estimates the impact of changing:

- Marketing spend
- Price
- Cost
- Demand

The model uses clear assumptions:

- Higher marketing spend can lift demand.
- Higher prices can reduce demand.
- Cost changes affect operating cost and cost of goods.
- Demand changes affect unit volume.

The output includes estimated revenue, profit, margin, risk level, and a recommended action.

### Recommendation Engine

`src/recommendation_engine.py` translates metrics into rule-based executive recommendations. It checks margin, profitability, growth trend, retention, regional performance, product mix, and scenario risk.

Each recommendation includes:

- Priority
- Theme
- Recommendation
- Reason

This keeps the logic explainable for interviews and business users.

## Why This Architecture Works

- It is simple enough to understand quickly.
- The business logic is testable without running Streamlit.
- SQLite makes the project feel like a real analytics app without requiring a cloud database.
- The recommendation engine makes the app decision-oriented instead of chart-only.
