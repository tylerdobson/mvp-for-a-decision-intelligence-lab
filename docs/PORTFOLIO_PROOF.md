# Validation Notes

This document explains how to verify that Retail KPI & Forecasting Sandbox is a working analytics product, not only a static code sample.

Finding: The recommendation engine flags low-margin, high-volume segments as a risk; one example action is to improve product economics before pushing more volume.

## Verification Checklist

- Dependencies install with `python -m pip install -r requirements.txt`.
- Database setup runs with `python scripts/setup_database.py`.
- SQLite loads 1,728 modeled retail operating records.
- Streamlit starts with `streamlit run app.py`.
- pytest passes.
- compileall passes.
- Media capture creates screenshots and video in `assets/demo/`.
- README media links resolve to real files.
- No credentials or private data are required.

## App Validation

The dashboard includes:

- Executive Overview with KPI cards and next action.
- KPI Explorer with filters and trend explanations.
- Revenue & Profit Trends with review-ready charts.
- Forecasting Lab with actual-vs-forecast view and limitation notes.
- Scenario Analysis with business controls, risk level, and recommendation.
- Executive Recommendations with priority, evidence, and action.
- Data Explorer with filtered table and CSV download.
- Export Center with CSV and Markdown outputs.

## Media Validation

The capture workflow writes:

- `assets/demo/hero.png`
- `assets/demo/dashboard-overview.png`
- `assets/demo/kpi-explorer.png`
- `assets/demo/forecasting-lab.png`
- `assets/demo/scenario-analysis.png`
- `assets/demo/executive-recommendations.png`
- `assets/demo/data-explorer.png`
- `assets/demo/demo-poster.png`
- `assets/demo/demo.webm`
- `assets/demo/demo.mp4` when `ffmpeg` is available
- `assets/demo/linkedin-cover.png`
- `assets/demo/media_manifest.json`

## How To Regenerate Validation Media

```bash
python -m playwright install chromium
python scripts/capture_decision_lab_media.py
```

The media script uses only modeled demo data and starts the app locally on a fixed port for capture.

## Project Positioning

Retail KPI & Forecasting Sandbox demonstrates:

- Analytics engineering
- Streamlit product design
- SQLite data persistence
- KPI calculation
- Forecasting with limitations
- Scenario modeling
- Explainable recommendation logic
- Automated validation media generation
