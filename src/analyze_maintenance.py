"""Analyze hotel maintenance work orders and create portfolio-ready outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "hotel_maintenance_work_orders.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

NAVY = "#14213D"
GOLD = "#FCA311"
BLUE = "#2F6690"
TEAL = "#4D9078"
RED = "#C44536"
LIGHT_GRAY = "#E5E5E5"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the CSV, validate key fields, and add analysis features."""
    data = pd.read_csv(path, parse_dates=["opened_at", "closed_at"])

    required_columns = {
        "work_order_id",
        "opened_at",
        "closed_at",
        "system_type",
        "maintenance_type",
        "priority",
        "shift",
        "asset_age_years",
        "response_minutes",
        "downtime_hours",
        "total_cost",
        "sla_met",
        "repeat_within_30_days",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset is missing required columns: {missing}")

    data["opened_month"] = data["opened_at"].dt.to_period("M").astype(str)
    data["opened_hour"] = data["opened_at"].dt.hour
    data["asset_age_group"] = pd.cut(
        data["asset_age_years"],
        bins=[0, 5, 10, 15, np.inf],
        labels=["1-5 years", "6-10 years", "11-15 years", "16+ years"],
    )
    return data


def calculate_kpis(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate the headline metrics used in the executive summary."""
    metrics = [
        ("Total work orders", len(data), "count"),
        ("Total maintenance cost", data["total_cost"].sum(), "currency"),
        ("Average response time", data["response_minutes"].mean(), "minutes"),
        ("SLA compliance rate", data["sla_met"].mean(), "percentage"),
        ("Repeat repair rate", data["repeat_within_30_days"].mean(), "percentage"),
        ("Average downtime", data["downtime_hours"].mean(), "hours"),
        ("Guest-impacting work orders", data["guest_impact"].mean(), "percentage"),
    ]
    return pd.DataFrame(metrics, columns=["metric", "value", "format"])


def build_summary_tables(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create reusable summary tables for systems, shifts, and asset age."""
    system_performance = (
        data.groupby("system_type", observed=True)
        .agg(
            work_orders=("work_order_id", "count"),
            total_cost=("total_cost", "sum"),
            average_cost=("total_cost", "mean"),
            average_downtime_hours=("downtime_hours", "mean"),
            sla_compliance=("sla_met", "mean"),
            repeat_rate=("repeat_within_30_days", "mean"),
            guest_impact_rate=("guest_impact", "mean"),
        )
        .sort_values("total_cost", ascending=False)
        .reset_index()
    )

    shift_performance = (
        data.groupby("shift", observed=True)
        .agg(
            work_orders=("work_order_id", "count"),
            average_response_minutes=("response_minutes", "mean"),
            sla_compliance=("sla_met", "mean"),
            guest_impact_work_orders=("guest_impact", "sum"),
        )
        .reindex(["Day", "Evening", "Overnight"])
        .reset_index()
    )

    maintenance_type = (
        data.groupby("maintenance_type", observed=True)
        .agg(
            work_orders=("work_order_id", "count"),
            average_cost=("total_cost", "mean"),
            average_downtime_hours=("downtime_hours", "mean"),
            repeat_rate=("repeat_within_30_days", "mean"),
        )
        .reset_index()
    )

    asset_age = (
        data.groupby("asset_age_group", observed=True)
        .agg(
            work_orders=("work_order_id", "count"),
            average_cost=("total_cost", "mean"),
            repeat_rate=("repeat_within_30_days", "mean"),
            average_downtime_hours=("downtime_hours", "mean"),
        )
        .reset_index()
    )

    monthly_trend = (
        data.groupby("opened_month", observed=True)
        .agg(
            work_orders=("work_order_id", "count"),
            total_cost=("total_cost", "sum"),
            sla_compliance=("sla_met", "mean"),
        )
        .reset_index()
    )

    return {
        "system_performance": system_performance,
        "shift_performance": shift_performance,
        "maintenance_type_performance": maintenance_type,
        "asset_age_performance": asset_age,
        "monthly_trend": monthly_trend,
    }


def create_charts(data: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    """Create four individual charts plus one executive dashboard."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")

    system = tables["system_performance"].sort_values("total_cost")
    shift = tables["shift_performance"]
    maintenance_type = tables["maintenance_type_performance"]
    asset_age = tables["asset_age_performance"]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(system["system_type"], system["total_cost"], color=BLUE)
    ax.set_title("Total Maintenance Cost by System", loc="left", weight="bold")
    ax.set_xlabel("Total cost ($)")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda value, _: f"${value / 1000:.0f}K")
    sns.despine()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cost_by_system.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [TEAL if value == shift["sla_compliance"].max() else GOLD for value in shift["sla_compliance"]]
    bars = ax.bar(shift["shift"], shift["sla_compliance"] * 100, color=colors)
    ax.bar_label(bars, labels=[f"{value:.1%}" for value in shift["sla_compliance"]], padding=3)
    ax.set_ylim(0, 100)
    ax.set_title("SLA Compliance by Shift", loc="left", weight="bold")
    ax.set_ylabel("Work orders meeting SLA (%)")
    ax.set_xlabel("")
    sns.despine()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "sla_by_shift.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    order = ["Preventive", "Corrective"]
    maintenance_plot = maintenance_type.set_index("maintenance_type").reindex(order).reset_index()
    bars = ax.bar(maintenance_plot["maintenance_type"], maintenance_plot["average_cost"], color=[TEAL, RED])
    ax.bar_label(bars, labels=[f"${value:,.0f}" for value in maintenance_plot["average_cost"]], padding=3)
    ax.set_title("Average Cost: Preventive vs. Corrective", loc="left", weight="bold")
    ax.set_ylabel("Average work-order cost ($)")
    ax.set_xlabel("")
    sns.despine()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cost_by_maintenance_type.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(asset_age["asset_age_group"].astype(str), asset_age["repeat_rate"] * 100, color=NAVY)
    ax.bar_label(bars, labels=[f"{value:.1%}" for value in asset_age["repeat_rate"]], padding=3)
    ax.set_title("Repeat Repairs Increase with Asset Age", loc="left", weight="bold")
    ax.set_ylabel("Repeat repair rate (%)")
    ax.set_xlabel("Asset age")
    sns.despine()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "repeat_rate_by_asset_age.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("Hotel Maintenance Operations Dashboard", fontsize=19, weight="bold", x=0.055, ha="left")

    axes[0, 0].barh(system["system_type"], system["total_cost"], color=BLUE)
    axes[0, 0].set_title("Total Cost by System", loc="left", weight="bold")
    axes[0, 0].set_xlabel("Total cost ($)")
    axes[0, 0].set_ylabel("")
    axes[0, 0].xaxis.set_major_formatter(lambda value, _: f"${value / 1000:.0f}K")

    axes[0, 1].bar(shift["shift"], shift["sla_compliance"] * 100, color=[TEAL, GOLD, RED])
    axes[0, 1].set_title("SLA Compliance by Shift", loc="left", weight="bold")
    axes[0, 1].set_ylabel("SLA compliance (%)")
    axes[0, 1].set_ylim(0, 100)
    axes[0, 1].set_xlabel("")

    axes[1, 0].bar(maintenance_plot["maintenance_type"], maintenance_plot["average_cost"], color=[TEAL, RED])
    axes[1, 0].set_title("Average Cost by Maintenance Type", loc="left", weight="bold")
    axes[1, 0].set_ylabel("Average cost ($)")
    axes[1, 0].set_xlabel("")

    axes[1, 1].bar(asset_age["asset_age_group"].astype(str), asset_age["repeat_rate"] * 100, color=NAVY)
    axes[1, 1].set_title("Repeat Repair Rate by Asset Age", loc="left", weight="bold")
    axes[1, 1].set_ylabel("Repeat rate (%)")
    axes[1, 1].set_xlabel("Asset age")

    for axis in axes.flat:
        axis.grid(axis="x" if axis in [axes[0, 0]] else "y", alpha=0.25)
    sns.despine(fig=fig)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(FIGURES_DIR / "executive_dashboard.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_executive_summary(data: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    """Write a concise business report using the calculated results."""
    system = tables["system_performance"]
    shift = tables["shift_performance"]
    maintenance_type = tables["maintenance_type_performance"].set_index("maintenance_type")
    asset_age = tables["asset_age_performance"].set_index("asset_age_group")

    top_cost_system = system.iloc[0]
    lowest_sla_shift = shift.loc[shift["sla_compliance"].idxmin()]
    preventive_cost = maintenance_type.loc["Preventive", "average_cost"]
    corrective_cost = maintenance_type.loc["Corrective", "average_cost"]
    cost_difference = 1 - preventive_cost / corrective_cost
    younger_repeat = asset_age.loc["1-5 years", "repeat_rate"]
    older_repeat = asset_age.loc["16+ years", "repeat_rate"]
    repeat_multiple = older_repeat / younger_repeat if younger_repeat else np.nan

    report = f"""# Executive Summary: Hotel Maintenance Operations

## Objective

Analyze 1,200 synthetic hotel maintenance work orders to identify opportunities to reduce response delays, repeat repairs, downtime, and operating cost while protecting the guest experience.

## Headline KPIs

| KPI | Result |
| --- | ---: |
| Total work orders | {len(data):,} |
| Total maintenance cost | ${data['total_cost'].sum():,.0f} |
| Average response time | {data['response_minutes'].mean():.1f} minutes |
| SLA compliance | {data['sla_met'].mean():.1%} |
| Repeat repair rate | {data['repeat_within_30_days'].mean():.1%} |
| Average downtime | {data['downtime_hours'].mean():.1f} hours |

## Key Findings

1. **{top_cost_system['system_type']} is the largest cost center.** It generated {int(top_cost_system['work_orders']):,} work orders and ${top_cost_system['total_cost']:,.0f} in maintenance cost.
2. **The {lowest_sla_shift['shift'].lower()} shift has the largest response opportunity.** Its SLA compliance was {lowest_sla_shift['sla_compliance']:.1%}, with an average response time of {lowest_sla_shift['average_response_minutes']:.1f} minutes.
3. **Preventive work is less expensive per event.** The average preventive work order cost ${preventive_cost:,.0f}, compared with ${corrective_cost:,.0f} for corrective work—a {cost_difference:.1%} difference. This is an association in the synthetic data, not proof that preventive maintenance alone caused the savings.
4. **Older assets show greater repeat-repair risk.** Assets 16+ years old had a {older_repeat:.1%} repeat rate versus {younger_repeat:.1%} for assets 1–5 years old ({repeat_multiple:.1f}x as high).

## Recommendations

- Prioritize an HVAC and refrigeration preventive-maintenance review, beginning with high-cost assets over 10 years old.
- Test flex coverage or an on-call escalation window for overnight high-priority requests, then compare SLA compliance before and after the change.
- Add a root-cause review for assets with a repeat work order within 30 days instead of treating each event as isolated.
- Track the same KPIs monthly: SLA compliance, response time, repeat rate, downtime, and cost by system.

## Data Note

This portfolio project uses synthetic data generated in `src/generate_data.py`. The workflow and business scenario are realistic, but the results do not describe an actual hotel or employer.
"""
    (REPORTS_DIR / "executive_summary.md").write_text(report, encoding="utf-8")


def save_outputs(kpis: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    """Save analysis tables as CSV files for review and reuse."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    kpis.to_csv(REPORTS_DIR / "kpi_summary.csv", index=False)
    for table_name, table in tables.items():
        table.to_csv(REPORTS_DIR / f"{table_name}.csv", index=False)


def main() -> None:
    """Run the complete analysis workflow."""
    data = load_data()
    kpis = calculate_kpis(data)
    tables = build_summary_tables(data)
    save_outputs(kpis, tables)
    create_charts(data, tables)
    write_executive_summary(data, tables)

    print("Analysis complete")
    print(f"Work orders: {len(data):,}")
    print(f"SLA compliance: {data['sla_met'].mean():.1%}")
    print(f"Repeat repair rate: {data['repeat_within_30_days'].mean():.1%}")
    print(f"Outputs saved to: {REPORTS_DIR}")


if __name__ == "__main__":
    main()
