# Portfolio Proof

This document explains how to verify that Decision Intelligence Lab is a working analytics product, not only a static code sample.

## Verification Checklist

- Dependencies install with `python -m pip install -r requirements.txt`.
- Database setup runs with `python scripts/setup_database.py`.
- SQLite loads 1,728 synthetic records.
- Streamlit starts with `streamlit run app.py`.
- pytest passes.
- compileall passes.
- Media capture creates screenshots and video in `assets/demo/`.
- README media links resolve to real files.
- No credentials or private data are required.

## App Proof

The dashboard includes:

- Executive Overview with KPI cards and next action.
- KPI Explorer with filters and trend explanations.
- Revenue & Profit Trends with portfolio-ready charts.
- Forecasting Lab with actual-vs-forecast view and limitation notes.
- Scenario Analysis with business controls, risk level, and recommendation.
- Executive Recommendations with priority, evidence, and action.
- Data Explorer with filtered table and CSV download.
- Export Center with CSV and Markdown outputs.

## Media Proof

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

## How To Regenerate Proof

```bash
python -m playwright install chromium
python scripts/capture_decision_lab_media.py
```

The media script uses only synthetic demo data and starts the app locally on a fixed port for capture.

## Portfolio Positioning

Decision Intelligence Lab demonstrates:

- Analytics engineering
- Streamlit product design
- SQLite data persistence
- KPI calculation
- Forecasting with limitations
- Scenario modeling
- Explainable recommendation logic
- Automated proof media generation
