# Setup Guide

Retail KPI & Forecasting Sandbox runs locally with Python, Streamlit, pandas, Plotly, SQLite, and pytest. It does not require external APIs, paid services, or credentials.

## Mac/Linux

```bash
git clone https://github.com/tylerdobson/mvp-for-a-decision-intelligence-lab.git
cd mvp-for-a-decision-intelligence-lab
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_database.py
streamlit run app.py
```

Open `http://localhost:8501`.

## Windows PowerShell

```powershell
git clone https://github.com/tylerdobson/mvp-for-a-decision-intelligence-lab.git
cd mvp-for-a-decision-intelligence-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\setup_database.py
streamlit run app.py
```

Open `http://localhost:8501`.

## Tests

```bash
python -m pytest
python -m compileall -q app.py src scripts tests
```

## Media Capture

Install the Playwright browser runtime once:

```bash
python -m playwright install chromium
```

Capture project media:

```bash
python scripts/capture_decision_lab_media.py
```

If `ffmpeg` is installed, the script writes both `demo.webm` and `demo.mp4`. If `ffmpeg` is not installed, the WebM video is kept.

## Troubleshooting

- If Streamlit cannot find data, run `python scripts/setup_database.py`.
- If Playwright reports missing Chromium, run `python -m playwright install chromium`.
- If MP4 conversion fails, use `assets/demo/demo.webm` or install `ffmpeg`.
- If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for that terminal session only.
