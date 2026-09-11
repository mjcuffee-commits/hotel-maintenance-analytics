"""Basic quality checks for the portfolio project."""

import json
from pathlib import Path
import sqlite3
import unittest

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "hotel_maintenance_work_orders.csv"
DATABASE_PATH = PROJECT_ROOT / "data" / "hotel_maintenance.db"
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "Hotel_Maintenance_Analysis.ipynb"


class ProjectQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = pd.read_csv(CSV_PATH, parse_dates=["opened_at", "closed_at"])

    def test_expected_row_count_and_unique_ids(self) -> None:
        self.assertEqual(len(self.data), 1_200)
        self.assertTrue(self.data["work_order_id"].is_unique)

    def test_dates_and_numeric_values_are_valid(self) -> None:
        self.assertTrue((self.data["closed_at"] >= self.data["opened_at"]).all())
        self.assertTrue((self.data["response_minutes"] > 0).all())
        self.assertTrue((self.data["total_cost"] >= 0).all())

    def test_categories_are_expected(self) -> None:
        self.assertEqual(
            set(self.data["shift"]),
            {"Day", "Evening", "Overnight"},
        )
        self.assertEqual(
            set(self.data["maintenance_type"]),
            {"Corrective", "Preventive"},
        )

    def test_sqlite_database_matches_csv(self) -> None:
        with sqlite3.connect(DATABASE_PATH) as connection:
            database_count = connection.execute(
                "SELECT COUNT(*) FROM work_orders"
            ).fetchone()[0]
        self.assertEqual(database_count, len(self.data))

    def test_notebook_is_valid_json(self) -> None:
        with NOTEBOOK_PATH.open(encoding="utf-8") as notebook_file:
            notebook = json.load(notebook_file)
        self.assertEqual(notebook["nbformat"], 4)
        self.assertGreaterEqual(len(notebook["cells"]), 10)


if __name__ == "__main__":
    unittest.main()
