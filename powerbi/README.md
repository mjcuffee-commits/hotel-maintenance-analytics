# Power BI Dashboard Build

This folder documents the planned Power BI extension of the hotel maintenance analytics project. The dashboard must be built and understood independently before it is presented as a portfolio skill.

## Intended Audience

Hotel director of engineering, operations leadership, and property management.

## Decision Questions

1. Which systems create the greatest cost and downtime?
2. Where is SLA performance weakest?
3. Which assets have the greatest repeat-repair risk?
4. How do preventive and corrective work compare?
5. Which operational change should leadership test first?

## Required Measures

- Total work orders
- Total cost
- Average response time
- Average downtime
- SLA compliance rate
- Repeat-repair rate
- Preventive work percentage
- Guest-impact work percentage

## Required Views

- Executive KPI summary
- Monthly performance trend
- Cost and downtime by system
- SLA performance by shift
- Preventive-versus-corrective comparison
- Repeat repairs by asset-age group

## Validation Standard

Every Power BI measure must be checked against an equivalent Python or SQL result before publication.

## Planned Deliverables

- `hotel_maintenance_operations_dashboard.pbix`
- `dashboard_overview.png`
- `measure_dictionary.md`
- A short dashboard walkthrough in the main README

