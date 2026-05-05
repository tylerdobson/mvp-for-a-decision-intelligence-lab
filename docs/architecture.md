# Architecture

Retail KPI & Forecasting Sandbox is intentionally small, modular, and explainable. The app separates storage, analytics logic, visualization, exports, and presentation so the project is easy to run, test, and discuss in interviews.

## System Flow

```text
scripts/generate_sample_data.py
  -> data/sample_business_data.csv
  -> scripts/setup_database.py
  -> database/decision_lab.db
  -> src/data_loader.py
  -> KPI, forecast, scenario, recommendation, chart, and export modules
  -> app.py Streamlit dashboard
```

## Components

### Streamlit Interface

`app.py` composes the dashboard sections, sidebar navigation, global filters, and calls into the business logic modules. It avoids embedding core formulas directly in the UI.

Dashboard sections:

- Executive Overview
- KPI Explorer
- Revenue & Profit Trends
- Forecasting Lab
- Scenario Analysis
- Executive Recommendations
- Data Explorer
- Export Center
- Methodology / Assumptions
- About This Project

### Data Layer

`src/database.py` manages SQLite connections, table creation, CSV loading, and query execution. `src/data_loader.py` loads the analytics table into pandas and applies dashboard filters.

### KPI Engine

`src/kpi_engine.py` calculates revenue, profit, margins, costs, units, average price, retention, churn risk, marketing efficiency, month-over-month change, and best/worst performers.

### Forecasting Engine

`src/forecasting.py` uses a transparent blend of a linear trend and recent moving average. It includes an uncertainty band based on residual variation and avoids unsupported claims.

### Scenario Engine

`src/scenario_engine.py` models directional impact from:

- Marketing spend change
- Price change
- Cost change
- Demand change
- Retention change

The output includes estimated revenue, profit, gross margin, retention, risk level, recommended action, and plain-English interpretation.

### Recommendation Engine

`src/recommendation_engine.py` applies explainable business rules to identify strengths, risks, and opportunities. Each recommendation includes priority, theme, recommendation, evidence, and action.

### Visualization And UI Modules

`src/charts.py` owns Plotly figure builders. `src/ui_components.py` owns reusable Streamlit UI and CSS. This keeps `app.py` focused on page composition.

### Export Module

`src/report_exporter.py` builds CSV exports and Markdown executive summaries for business handoff.

### Media Workflow

`scripts/capture_decision_lab_media.py` starts the app, captures screenshots and a walkthrough video with Playwright, writes `assets/demo/media_manifest.json`, and converts WebM to MP4 when `ffmpeg` is available.

## Design Principles

- Decision support over chart dumping.
- Explainable formulas over black-box complexity.
- Synthetic public-safe data only.
- Local-first setup with no API keys.
- Tests for business logic.
- Validation media that the app actually runs.
