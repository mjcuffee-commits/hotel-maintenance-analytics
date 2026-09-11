"""Reproduce the full Hotel Maintenance Operations Analytics project."""

from src.analyze_maintenance import main as run_analysis
from src.build_database import build_database
from src.generate_data import main as generate_data


def main() -> None:
    print("1/3 Generating synthetic data...")
    generate_data()
    print("2/3 Running Python analysis...")
    run_analysis()
    print("3/3 Building SQLite database...")
    database_path = build_database()
    print(f"Project complete. Database: {database_path}")


if __name__ == "__main__":
    main()
