"""Capture project screenshots and video for Retail KPI & Forecasting Sandbox.

The script starts the Streamlit app, captures public-safe demo screenshots with
Playwright, records a short walkthrough video, and writes a media manifest.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEDIA_DIR = PROJECT_ROOT / "assets" / "demo"
PORT = 8509
BASE_URL = f"http://127.0.0.1:{PORT}"
VIEWPORT = {"width": 1600, "height": 1000}
VIDEO_SIZE = {"width": 1600, "height": 1000}

SCREENSHOTS = [
    ("hero.png", "executive-overview"),
    ("dashboard-overview.png", "executive-overview"),
    ("kpi-explorer.png", "kpi-explorer"),
    ("forecasting-lab.png", "forecasting-lab"),
    ("scenario-analysis.png", "scenario-analysis"),
    ("executive-recommendations.png", "executive-recommendations"),
    ("data-explorer.png", "data-explorer"),
]


def main() -> int:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_playwright()
    _run_database_setup()
    process = _start_streamlit()
    try:
        _wait_for_app()
        media = _capture_media()
        _write_manifest(media)
    finally:
        _stop_process(process)
    print(f"Media capture complete: {MEDIA_DIR}")
    return 0


def _ensure_playwright() -> None:
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        raise SystemExit(
            "Playwright is not installed. Run:\n"
            "python -m pip install -r requirements.txt\n"
            "python -m playwright install chromium"
        )


def _run_database_setup() -> None:
    command = [sys.executable, str(PROJECT_ROOT / "scripts" / "setup_database.py")]
    result = subprocess.run(command, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            "Database setup failed before media capture.\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def _start_streamlit() -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_ROOT / "app.py"),
        "--server.port",
        str(PORT),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--global.developmentMode",
        "false",
    ]
    return subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _wait_for_app(timeout_seconds: int = 60) -> None:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            with urlopen(BASE_URL, timeout=2) as response:
                if response.status == 200:
                    return
        except URLError as exc:
            last_error = str(exc)
        time.sleep(1)
    raise SystemExit(
        f"Streamlit did not respond at {BASE_URL} within {timeout_seconds} seconds. "
        f"Last error: {last_error}"
    )


def _capture_media() -> list[dict[str, str | int]]:
    from playwright.sync_api import Error, sync_playwright

    captured: list[dict[str, str | int]] = []
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Error as exc:
            raise SystemExit(
                "Chromium is not installed for Playwright. Run:\n"
                "python -m playwright install chromium\n"
                f"Original error: {exc}"
            )

        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=2,
            record_video_dir=str(MEDIA_DIR),
            record_video_size=VIDEO_SIZE,
        )
        page = context.new_page()
        for filename, section in SCREENSHOTS:
            _open_section(page, section)
            path = MEDIA_DIR / filename
            page.screenshot(path=str(path), full_page=False)
            _assert_non_empty(path)
            captured.append({"file": filename, "bytes": path.stat().st_size})

        for _, section in SCREENSHOTS[:6]:
            _open_section(page, section)
            page.wait_for_timeout(2200)

        video = page.video
        context.close()
        browser.close()

        webm_path = MEDIA_DIR / "demo.webm"
        if video:
            recorded_path = Path(video.path())
            if webm_path.exists():
                webm_path.unlink()
            shutil.move(str(recorded_path), webm_path)
            _assert_non_empty(webm_path)
            captured.append({"file": "demo.webm", "bytes": webm_path.stat().st_size})

        _create_poster_assets(captured)
        _convert_to_mp4_if_available(webm_path, captured)
    return captured


def _open_section(page, section: str) -> None:
    page.goto(f"{BASE_URL}/?section={section}", wait_until="domcontentloaded")
    deadline = time.time() + 45
    while time.time() < deadline:
        try:
            body_text = page.locator("body").inner_text(timeout=2_000)
            if "Retail KPI & Forecasting Sandbox" in body_text:
                break
        except Exception:
            pass
        page.wait_for_timeout(1_000)
    else:
        raise SystemExit(
            f"Streamlit loaded at {BASE_URL}, but the dashboard text did not render for section '{section}'. "
            "Open the app manually and check for a Streamlit error screen."
        )
    page.wait_for_timeout(1200)


def _assert_non_empty(path: Path) -> None:
    if not path.exists() or path.stat().st_size < 10_000:
        raise SystemExit(f"Expected media file was missing or too small: {path}")


def _create_poster_assets(captured: list[dict[str, str | int]]) -> None:
    poster = MEDIA_DIR / "demo-poster.png"
    cover = MEDIA_DIR / "linkedin-cover.png"
    source = MEDIA_DIR / "dashboard-overview.png"
    shutil.copyfile(source, poster)
    shutil.copyfile(source, cover)
    captured.append({"file": "demo-poster.png", "bytes": poster.stat().st_size})
    captured.append({"file": "linkedin-cover.png", "bytes": cover.stat().st_size})


def _convert_to_mp4_if_available(webm_path: Path, captured: list[dict[str, str | int]]) -> None:
    if not webm_path.exists():
        return
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ffmpeg was not found. Keeping demo.webm only.")
        return
    mp4_path = MEDIA_DIR / "demo.mp4"
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(webm_path),
        "-movflags",
        "+faststart",
        "-pix_fmt",
        "yuv420p",
        str(mp4_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpeg conversion failed. Keeping demo.webm only.")
        print(result.stderr)
        return
    _assert_non_empty(mp4_path)
    captured.append({"file": "demo.mp4", "bytes": mp4_path.stat().st_size})


def _write_manifest(media: list[dict[str, str | int]]) -> None:
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "app_url": BASE_URL,
        "viewport": VIEWPORT,
        "device_scale_factor": 2,
        "media": media,
        "notes": "Synthetic demo data only. Forecasts are directional and not guaranteed predictions.",
    }
    path = MEDIA_DIR / "media_manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
