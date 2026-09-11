"""Load the project CSV into a local SQLite database for SQL practice."""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "hotel_maintenance_work_orders.csv"
DATABASE_PATH = PROJECT_ROOT / "data" / "hotel_maintenance.db"


def build_database() -> Path:
    """Create or replace the work_orders table and return the database path."""
    data = pd.read_csv(CSV_PATH)
    boolean_columns = [
        "guest_impact",
        "room_out_of_order",
        "sla_met",
        "repeat_within_30_days",
    ]
    for column in boolean_columns:
        data[column] = data[column].astype(int)

    with sqlite3.connect(DATABASE_PATH) as connection:
        data.to_sql("work_orders", connection, if_exists="replace", index=False)
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_work_order_id "
            "ON work_orders(work_order_id)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_system_type "
            "ON work_orders(system_type)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_opened_at "
            "ON work_orders(opened_at)"
        )

    return DATABASE_PATH


if __name__ == "__main__":
    path = build_database()
    print(f"Created SQLite database at {path}")
