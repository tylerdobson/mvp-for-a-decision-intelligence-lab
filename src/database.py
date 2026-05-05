"""SQLite database utilities for Retail KPI & Forecasting Sandbox."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.utils import PROJECT_ROOT


DEFAULT_DB_PATH = PROJECT_ROOT / "database" / "decision_lab.db"
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "sql" / "create_tables.sql"
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "sample_business_data.csv"
TABLE_NAME = "business_metrics"


def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with row-friendly defaults."""

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def create_database(
    db_path: Path | str = DEFAULT_DB_PATH,
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
) -> None:
    """Create the database schema from the SQL file."""

    db_path = Path(db_path)
    schema_path = Path(schema_path)
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with get_connection(db_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))


def load_csv_to_database(
    csv_path: Path | str = DEFAULT_DATA_PATH,
    db_path: Path | str = DEFAULT_DB_PATH,
    table_name: str = TABLE_NAME,
) -> int:
    """Load the sample CSV into SQLite and return the number of rows loaded."""

    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    expected_columns = {
        "month",
        "region",
        "product_category",
        "customer_segment",
        "marketing_spend",
        "operating_cost",
        "units_sold",
        "average_price",
        "revenue",
        "gross_margin_rate",
        "gross_margin",
        "profit",
        "retention_rate",
        "churn_risk",
    }
    missing_columns = expected_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV is missing required columns: {missing}")

    with get_connection(db_path) as connection:
        df.to_sql(table_name, connection, if_exists="append", index=False)
        row_count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    return int(row_count)


def initialize_database(
    db_path: Path | str = DEFAULT_DB_PATH,
    csv_path: Path | str = DEFAULT_DATA_PATH,
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
    reset: bool = True,
) -> int:
    """Create the SQLite database and load sample business data."""

    db_path = Path(db_path)
    if reset and db_path.exists():
        db_path.unlink()

    create_database(db_path=db_path, schema_path=schema_path)
    return load_csv_to_database(csv_path=csv_path, db_path=db_path)


def ensure_database(db_path: Path | str = DEFAULT_DB_PATH) -> Path:
    """Create the default database if it does not exist."""

    db_path = Path(db_path)
    if not db_path.exists():
        if not DEFAULT_DATA_PATH.exists():
            from scripts.generate_sample_data import generate_sample_data

            generate_sample_data(DEFAULT_DATA_PATH)
        initialize_database(db_path=db_path)
    return db_path


def query_dataframe(
    query: str,
    params: tuple | dict | None = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Run a SQL query and return a pandas DataFrame."""

    with get_connection(db_path) as connection:
        return pd.read_sql_query(query, connection, params=params)
