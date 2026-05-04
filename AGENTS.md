# AGENTS.md

Guidance for future Codex agents working in this repository.

## Project Purpose

Decision Intelligence Lab is a Streamlit analytics product that turns synthetic business data into KPIs, forecasts, scenario analysis, exports, and executive recommendations. Keep the project practical, explainable, and portfolio-ready.

## Core Commands

Install:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Database setup:

```bash
python scripts/setup_database.py
```

Run app:

```bash
streamlit run app.py
```

Run tests:

```bash
python -m pytest
python -m compileall -q app.py src scripts tests
```

Capture portfolio media:

```bash
python -m playwright install chromium
python scripts/capture_decision_lab_media.py
```

## Repo Structure Notes

- `app.py` owns Streamlit page composition and section routing.
- `src/kpi_engine.py` calculates KPIs and trend aggregates.
- `src/forecasting.py` contains the transparent forecast method.
- `src/scenario_engine.py` contains scenario assumptions and impact math.
- `src/recommendation_engine.py` contains rule-based recommendation logic.
- `src/charts.py` contains Plotly chart builders.
- `src/ui_components.py` contains shared Streamlit UI components and CSS.
- `src/report_exporter.py` contains CSV and Markdown export helpers.
- `scripts/generate_sample_data.py` creates synthetic data.
- `scripts/setup_database.py` rebuilds the SQLite database.
- `scripts/capture_decision_lab_media.py` regenerates README media.

## Coding Standards

- Keep business logic in `src/`, not embedded in Streamlit callbacks.
- Keep recommendations rule-based, explainable, and tied to visible metrics.
- Prefer readable formulas over fake complexity.
- Do not introduce external APIs, paid services, or credentials.
- Add or update tests when KPI, forecast, scenario, recommendation, or export logic changes.
- Do not change unrelated functionality while fixing a specific issue.

## Dashboard Quality Standards

- The app should feel like a decision-support product, not a rough class assignment.
- Avoid raw dataframe dumps as the primary UI.
- Use clear business language, captions, and limitations.
- Keep charts readable at GitHub screenshot size.
- Keep scenario analysis and recommendations tied to actionable decisions.
- Do not claim forecasts are guaranteed.

## Documentation Standards

- Keep README commands accurate and runnable.
- Keep media links in README pointed at `assets/demo/`.
- Update `docs/DATA_DICTIONARY.md` whenever dataset columns change.
- Update `docs/METHODOLOGY.md` when forecast, scenario, or recommendation rules change.
- Keep LinkedIn and GitHub post copy professional and non-hype.

## Safety Rules

- Do not commit `.env`, secrets, API keys, dependency folders, virtual environments, logs, or caches.
- The dataset is synthetic. Do not add private or real financial data.
- Do not delete files unless they are clearly generated artifacts.
- Do not overwrite documentation or media standards without updating README references.

## Definition Of Done

- Dependencies install.
- Database setup creates 1,728 rows.
- Streamlit starts without crashing.
- Tests pass.
- Media capture creates screenshots and a webm or mp4 demo.
- README media links resolve.
- No secrets are introduced.
