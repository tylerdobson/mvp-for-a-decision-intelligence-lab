# AGENTS.md

Guidance for future Codex agents working in this repository.

## Project Purpose

Decision Intelligence Lab is a Streamlit analytics app that turns sample business data into KPIs, forecasts, scenario analysis, and executive recommendations. Keep the project practical, explainable, and portfolio-ready.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_database.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\setup_database.py
```

## Run The App

```bash
streamlit run app.py
```

## Run Tests

```bash
python -m pytest
```

## Coding Standards

- Keep business logic in `src/`, not inside `app.py`.
- Keep recommendations rule-based and explainable.
- Avoid external APIs, paid services, or key-based dependencies.
- Prefer readable formulas over fake complexity.
- Add or update tests when changing KPI, scenario, or recommendation logic.
- Do not change unrelated functionality while fixing a specific issue.

## Documentation Standards

- Keep README instructions accurate and runnable.
- Update `docs/data_dictionary.md` whenever data columns change.
- Update `docs/architecture.md` when module responsibilities change.
- Keep business explanations clear enough for recruiters, students, and non-technical stakeholders.

## Data And Database Notes

- `scripts/generate_sample_data.py` creates `data/sample_business_data.csv`.
- `scripts/setup_database.py` rebuilds `database/decision_lab.db`.
- `sql/create_tables.sql` is the source of truth for the SQLite schema.
- Do not hand-edit the SQLite database unless debugging a database-specific issue.
