"""Create and seed the local SQLite database."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from generate_sample_data import generate_sample_data  # noqa: E402
from src.database import DEFAULT_DATA_PATH, DEFAULT_DB_PATH, initialize_database  # noqa: E402


def main() -> None:
    """Generate the CSV if needed, then rebuild the SQLite database."""

    if not DEFAULT_DATA_PATH.exists():
        generate_sample_data(DEFAULT_DATA_PATH)

    row_count = initialize_database(
        db_path=DEFAULT_DB_PATH,
        csv_path=DEFAULT_DATA_PATH,
        reset=True,
    )
    print(f"SQLite database created: {DEFAULT_DB_PATH}")
    print(f"Rows loaded into business_metrics: {row_count:,}")


if __name__ == "__main__":
    main()
