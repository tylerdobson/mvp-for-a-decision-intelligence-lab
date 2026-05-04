# Decision Intelligence Lab

Decision Intelligence Lab is a reusable analytics MVP that turns business data into KPIs, forecasts, scenario analysis, and executive-style recommendations. The goal is not just to display charts. The app helps answer: "What decision should someone make next?"

## Business Problem

Small teams often have sales, cost, marketing, and retention data but no clear decision workflow. This project shows how an analyst can move from raw business records to practical recommendations:

- Where is performance strongest?
- Which categories or regions deserve more focus?
- Are costs weakening profit?
- What might happen if price, cost, demand, or marketing spend changes?
- What action should leadership consider next?

## Features

- Streamlit dashboard with five decision sections.
- SQLite database for local analytics storage.
- Deterministic sample business dataset with 1,728 records.
- KPI engine for revenue, profit, margin, cost, units, retention, churn risk, and month-over-month change.
- Forecasting module using a transparent linear trend and moving-average blend.
- Scenario analysis for marketing spend, price, cost, and demand changes.
- Rule-based recommendation engine with High, Medium, and Low priorities.
- SQL files for schema creation and analysis examples.
- Tests for KPI, scenario, and recommendation logic.
- Documentation designed for GitHub, LinkedIn, and internship interviews.

## Tech Stack

- Python
- Streamlit
- pandas
- SQLite
- Plotly
- NumPy
- pytest

## Screenshots

Add screenshots to `assets/screenshots/` after running the app locally.

Recommended screenshots:

1. Executive Overview with the headline KPI cards and trend chart.
2. KPI Explorer with filters open in the sidebar.
3. Forecasting tab showing the revenue forecast and uncertainty band.
4. Scenario Analysis after changing the sliders.
5. Executive Recommendations showing priority cards.

## How To Run Locally

```bash
git clone <your-repo-url>
cd decision-intelligence-lab
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_database.py
streamlit run app.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\setup_database.py
streamlit run app.py
```

## Run Tests

```bash
python -m pytest
```

## Project Structure

```text
decision-intelligence-lab/
  README.md
  AGENTS.md
  requirements.txt
  app.py
  data/
    sample_business_data.csv
  database/
    decision_lab.db
  src/
    data_loader.py
    database.py
    kpi_engine.py
    forecasting.py
    scenario_engine.py
    recommendation_engine.py
    utils.py
  sql/
    create_tables.sql
    seed_data.sql
    analysis_queries.sql
  tests/
    test_kpi_engine.py
    test_scenario_engine.py
    test_recommendation_engine.py
  docs/
    architecture.md
    data_dictionary.md
    business_use_case.md
    interview_explanation.md
  assets/
    screenshots/
  scripts/
    setup_database.py
    generate_sample_data.py
```

## What Decisions The App Supports

- Increase or reduce marketing spend by region or category.
- Investigate products with high volume but weak margins.
- Monitor cost pressure when profit falls faster than revenue.
- Prioritize retention when churn risk rises.
- Test pricing or demand scenarios before making operational changes.
- Communicate recommendations in executive language with metric evidence.

## Example Use Cases

- A student analyst demonstrating business analytics skills.
- A small business owner reviewing revenue and margin drivers.
- A portfolio project for internship applications.
- A reusable starter pattern for KPI dashboards with recommendation logic.

## Important Assumptions

- Forecasts are directional planning estimates, not guaranteed predictions.
- Scenario analysis uses simple elasticity assumptions for explainability.
- Recommendations are rule-based and tied to visible metrics.
- The sample dataset is synthetic and should not be used for real financial decisions.
- The sample CSV and SQLite database can be regenerated locally with `python scripts/setup_database.py`.

## Future Improvements

- Add authenticated data upload for user-owned CSV files.
- Add a richer scenario model with product-level elasticity assumptions.
- Add automated screenshot generation for README assets.
- Add exportable executive summary reports.
- Add anomaly detection for unusual cost or retention changes.
- Add a Dockerfile for consistent deployment.
