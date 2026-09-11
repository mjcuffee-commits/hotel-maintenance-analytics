"""Generate a realistic, synthetic hotel maintenance work-order dataset.

The data is intentionally synthetic so the project can be shared publicly.
Patterns are built into the generator to make the analysis useful: older HVAC
and refrigeration assets fail more often, overnight coverage affects response
times, and preventive work costs less than corrective work.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 91
N_WORK_ORDERS = 1_200

SYSTEMS = [
    "HVAC",
    "Plumbing",
    "Electrical",
    "Refrigeration",
    "General Maintenance",
    "Life Safety",
]

SYSTEM_PROBABILITIES = [0.30, 0.22, 0.16, 0.12, 0.14, 0.06]

ISSUES = {
    "HVAC": [
        "Room not cooling",
        "Thermostat fault",
        "Fan motor failure",
        "Filter replacement",
        "Condensate leak",
    ],
    "Plumbing": [
        "Drain blockage",
        "Fixture leak",
        "Low water pressure",
        "No hot water",
        "Preventive inspection",
    ],
    "Electrical": [
        "Outlet failure",
        "Lighting outage",
        "Breaker trip",
        "Control panel fault",
        "Preventive inspection",
    ],
    "Refrigeration": [
        "Temperature above range",
        "Compressor fault",
        "Door seal failure",
        "Ice buildup",
        "Coil cleaning",
    ],
    "General Maintenance": [
        "Door hardware",
        "Furniture repair",
        "Wall or ceiling damage",
        "Signage repair",
        "Preventive inspection",
    ],
    "Life Safety": [
        "Alarm device fault",
        "Emergency light failure",
        "Sprinkler inspection",
        "Exit sign failure",
        "Panel communication fault",
    ],
}

AREAS_BY_SYSTEM = {
    "HVAC": (["Guest Room", "Meeting Space", "Lobby", "Mechanical Room", "Kitchen"], [0.55, 0.14, 0.10, 0.16, 0.05]),
    "Plumbing": (["Guest Room", "Kitchen", "Laundry", "Lobby", "Mechanical Room"], [0.55, 0.13, 0.13, 0.08, 0.11]),
    "Electrical": (["Guest Room", "Meeting Space", "Lobby", "Kitchen", "Exterior"], [0.42, 0.20, 0.14, 0.12, 0.12]),
    "Refrigeration": (["Kitchen", "Laundry", "Mechanical Room", "Meeting Space"], [0.69, 0.08, 0.18, 0.05]),
    "General Maintenance": (["Guest Room", "Meeting Space", "Lobby", "Exterior", "Kitchen"], [0.48, 0.15, 0.15, 0.12, 0.10]),
    "Life Safety": (["Guest Room", "Meeting Space", "Lobby", "Mechanical Room", "Exterior"], [0.28, 0.20, 0.18, 0.22, 0.12]),
}

SLA_TARGETS = {"Emergency": 15, "High": 30, "Medium": 120, "Low": 240}


def choose_priority(rng: np.random.Generator, maintenance_type: str, system: str) -> str:
    """Choose a priority based on maintenance type and system criticality."""
    if maintenance_type == "Preventive":
        return rng.choice(["High", "Medium", "Low"], p=[0.03, 0.42, 0.55])

    probabilities = np.array([0.10, 0.30, 0.45, 0.15])
    if system in {"HVAC", "Refrigeration", "Life Safety"}:
        probabilities += np.array([0.04, 0.05, -0.05, -0.04])
    probabilities = probabilities / probabilities.sum()
    return rng.choice(["Emergency", "High", "Medium", "Low"], p=probabilities)


def choose_opened_at(rng: np.random.Generator) -> pd.Timestamp:
    """Generate a 2025 timestamp with realistic hotel request peaks."""
    start = pd.Timestamp("2025-01-01")
    day_offset = int(rng.integers(0, 365))
    hour = int(
        rng.choice(
            np.arange(24),
            p=np.array(
                [
                    0.025,
                    0.018,
                    0.014,
                    0.012,
                    0.013,
                    0.018,
                    0.030,
                    0.045,
                    0.060,
                    0.070,
                    0.070,
                    0.060,
                    0.050,
                    0.045,
                    0.045,
                    0.050,
                    0.060,
                    0.065,
                    0.065,
                    0.060,
                    0.050,
                    0.040,
                    0.030,
                    0.025,
                ]
            )
            / 1.02,
        )
    )
    minute = int(rng.integers(0, 60))
    return start + pd.Timedelta(days=day_offset, hours=hour, minutes=minute)


def get_shift(hour: int) -> str:
    """Map the opened hour to a hotel engineering shift."""
    if 7 <= hour < 15:
        return "Day"
    if 15 <= hour < 23:
        return "Evening"
    return "Overnight"


def generate_work_orders(n_rows: int = N_WORK_ORDERS, seed: int = SEED) -> pd.DataFrame:
    """Return a reproducible DataFrame of hotel maintenance work orders."""
    rng = np.random.default_rng(seed)
    records: list[dict[str, object]] = []

    response_base = {"Emergency": 11, "High": 24, "Medium": 67, "Low": 145}
    repair_base = {
        "HVAC": 105,
        "Plumbing": 82,
        "Electrical": 76,
        "Refrigeration": 128,
        "General Maintenance": 48,
        "Life Safety": 92,
    }
    parts_base = {
        "HVAC": 155,
        "Plumbing": 80,
        "Electrical": 92,
        "Refrigeration": 205,
        "General Maintenance": 42,
        "Life Safety": 115,
    }
    repeat_base = {
        "HVAC": 0.12,
        "Plumbing": 0.09,
        "Electrical": 0.07,
        "Refrigeration": 0.14,
        "General Maintenance": 0.05,
        "Life Safety": 0.05,
    }

    for index in range(1, n_rows + 1):
        system = str(rng.choice(SYSTEMS, p=SYSTEM_PROBABILITIES))
        maintenance_type = str(rng.choice(["Corrective", "Preventive"], p=[0.78, 0.22]))
        priority = choose_priority(rng, maintenance_type, system)
        opened_at = choose_opened_at(rng)
        shift = get_shift(opened_at.hour)

        area_names, area_probabilities = AREAS_BY_SYSTEM[system]
        property_area = str(rng.choice(area_names, p=area_probabilities))

        asset_age_years = int(np.clip(rng.normal(8.5 if system == "HVAC" else 6.8, 4.2), 1, 20))

        guest_probability = 0.08
        if property_area == "Guest Room":
            guest_probability += 0.52
        if system in {"HVAC", "Plumbing", "Electrical"}:
            guest_probability += 0.10
        if priority in {"Emergency", "High"}:
            guest_probability += 0.12
        guest_impact = bool(rng.random() < min(guest_probability, 0.90))

        shift_multiplier = {"Day": 0.92, "Evening": 1.05, "Overnight": 1.32}[shift]
        response_minutes = response_base[priority] * shift_multiplier
        response_minutes *= 0.83 if guest_impact else 1.0
        response_minutes *= rng.lognormal(mean=0.0, sigma=0.34)
        response_minutes = max(3, int(round(response_minutes)))

        repair_minutes = repair_base[system]
        repair_minutes *= {"Emergency": 1.18, "High": 1.08, "Medium": 1.0, "Low": 0.86}[priority]
        repair_minutes *= 0.72 if maintenance_type == "Preventive" else 1.0
        repair_minutes *= 1 + max(asset_age_years - 8, 0) * 0.025
        repair_minutes *= rng.lognormal(mean=0.0, sigma=0.30)
        repair_minutes = max(12, int(round(repair_minutes)))

        age_effect = max(asset_age_years - 8, 0) * 0.012
        repeat_probability = repeat_base[system] + age_effect
        if maintenance_type == "Preventive":
            repeat_probability *= 0.28
        if priority == "Emergency":
            repeat_probability += 0.035
        repeat_within_30_days = bool(rng.random() < min(repeat_probability, 0.38))

        parts_cost = parts_base[system] * rng.gamma(shape=1.65, scale=0.62)
        parts_cost *= 0.42 if maintenance_type == "Preventive" else 1.0
        parts_cost *= 1 + max(asset_age_years - 10, 0) * 0.035
        parts_cost = round(parts_cost, 2)

        labor_hours = round(repair_minutes / 60, 2)
        labor_cost = round(labor_hours * 38.50, 2)
        total_cost = round(parts_cost + labor_cost, 2)

        sla_target_minutes = SLA_TARGETS[priority]
        sla_met = response_minutes <= sla_target_minutes
        downtime_hours = round((response_minutes + repair_minutes) / 60, 2)
        closed_at = opened_at + pd.Timedelta(minutes=response_minutes + repair_minutes)

        room_out_of_order = bool(
            property_area == "Guest Room"
            and guest_impact
            and priority in {"Emergency", "High"}
            and rng.random() < 0.62
        )

        if guest_impact:
            rating = 4.75
            rating -= 0.85 if not sla_met else 0
            rating -= min(downtime_hours / 8, 0.65)
            rating += rng.normal(0, 0.33)
            guest_satisfaction = round(float(np.clip(rating, 1.0, 5.0)), 1)
        else:
            guest_satisfaction = np.nan

        technicians = {
            "Day": ["ENG-01", "ENG-02", "ENG-03", "ENG-04"],
            "Evening": ["ENG-05", "ENG-06", "ENG-07"],
            "Overnight": ["ENG-08", "ENG-09"],
        }
        technician_id = str(rng.choice(technicians[shift]))

        issue_type = str(rng.choice(ISSUES[system]))
        if maintenance_type == "Preventive" and "Preventive inspection" in ISSUES[system]:
            issue_type = "Preventive inspection"

        records.append(
            {
                "work_order_id": f"WO-{index:05d}",
                "opened_at": opened_at,
                "closed_at": closed_at,
                "property_area": property_area,
                "system_type": system,
                "issue_type": issue_type,
                "maintenance_type": maintenance_type,
                "priority": priority,
                "shift": shift,
                "technician_id": technician_id,
                "asset_age_years": asset_age_years,
                "guest_impact": guest_impact,
                "room_out_of_order": room_out_of_order,
                "response_minutes": response_minutes,
                "repair_minutes": repair_minutes,
                "downtime_hours": downtime_hours,
                "labor_hours": labor_hours,
                "parts_cost": parts_cost,
                "labor_cost": labor_cost,
                "total_cost": total_cost,
                "sla_target_minutes": sla_target_minutes,
                "sla_met": sla_met,
                "repeat_within_30_days": repeat_within_30_days,
                "guest_satisfaction": guest_satisfaction,
            }
        )

    data = pd.DataFrame(records).sort_values("opened_at").reset_index(drop=True)
    return data


def main() -> None:
    """Generate the dataset and save it in the project's data directory."""
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "hotel_maintenance_work_orders.csv"
    data = generate_work_orders()
    data.to_csv(output_path, index=False, date_format="%Y-%m-%d %H:%M:%S")
    print(f"Created {len(data):,} synthetic work orders at {output_path}")


if __name__ == "__main__":
    main()
