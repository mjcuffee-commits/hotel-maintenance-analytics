# Executive Summary: Hotel Maintenance Operations

## Objective

Analyze 1,200 synthetic hotel maintenance work orders to identify opportunities to reduce response delays, repeat repairs, downtime, and operating cost while protecting the guest experience.

## Headline KPIs

| KPI | Result |
| --- | ---: |
| Total work orders | 1,200 |
| Total maintenance cost | $194,237 |
| Average response time | 68.5 minutes |
| SLA compliance | 90.0% |
| Repeat repair rate | 10.8% |
| Average downtime | 2.6 hours |

## Key Findings

1. **HVAC is the largest cost center.** It generated 345 work orders and $69,750 in maintenance cost.
2. **The overnight shift has the largest response opportunity.** Its SLA compliance was 74.0%, with an average response time of 81.8 minutes.
3. **Preventive work is less expensive per event.** The average preventive work order cost $91, compared with $183 for corrective work—a 50.2% difference. This is an association in the synthetic data, not proof that preventive maintenance alone caused the savings.
4. **Older assets show greater repeat-repair risk.** Assets 16+ years old had a 33.3% repeat rate versus 8.4% for assets 1–5 years old (4.0x as high).

## Recommendations

- Prioritize an HVAC and refrigeration preventive-maintenance review, beginning with high-cost assets over 10 years old.
- Test flex coverage or an on-call escalation window for overnight high-priority requests, then compare SLA compliance before and after the change.
- Add a root-cause review for assets with a repeat work order within 30 days instead of treating each event as isolated.
- Track the same KPIs monthly: SLA compliance, response time, repeat rate, downtime, and cost by system.

## Data Note

This portfolio project uses synthetic data generated in `src/generate_data.py`. The workflow and business scenario are realistic, but the results do not describe an actual hotel or employer.
