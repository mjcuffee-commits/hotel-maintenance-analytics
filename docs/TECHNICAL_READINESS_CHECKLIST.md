# Operations BI Technical Readiness Checklist

Use this checklist to decide whether a skill has been learned—not merely viewed in a lesson.

## SQL

- [ ] Select, filter, sort, and limit records.
- [ ] Use `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX`.
- [ ] Use `GROUP BY` and `HAVING` correctly.
- [ ] Join two or more tables and explain the join key.
- [ ] Use `CASE` to create business categories.
- [ ] Write subqueries and common table expressions.
- [ ] Use date functions for weekly and monthly reporting.
- [ ] Use window functions for ranking, running totals, and comparisons.
- [ ] Check for nulls, duplicates, and impossible values.
- [ ] Explain how each query supports a business decision.

### SQL proof

- [ ] Complete three practice sessions in a normal week.
- [ ] Answer five maintenance questions using `sql/maintenance_analysis.sql`.
- [ ] Rewrite the main queries without looking at the existing file.
- [ ] Complete a timed SQL practice set and review every error.

## Power BI

- [ ] Import CSV and database data.
- [ ] Clean and transform fields with Power Query.
- [ ] Build and explain table relationships.
- [ ] Create explicit DAX measures rather than relying only on automatic aggregation.
- [ ] Build KPI cards, trend charts, comparison charts, and useful slicers.
- [ ] Apply consistent formatting and readable titles.
- [ ] Add tooltips or drill-through only when they answer a business question.
- [ ] Validate every displayed number against Python or SQL output.
- [ ] Export a clear dashboard image for the repository.
- [ ] Explain what decision each visual supports.

### Required maintenance dashboard KPIs

- [ ] Total work orders
- [ ] Total maintenance cost
- [ ] Average downtime
- [ ] SLA compliance rate
- [ ] Repeat-repair rate
- [ ] Preventive-versus-corrective comparison
- [ ] Performance by system and shift
- [ ] Performance by asset-age group

## Python and pandas

- [ ] Load CSV data with pandas.
- [ ] Inspect shape, columns, types, and missing values.
- [ ] Convert date and numeric columns safely.
- [ ] Filter rows and create calculated columns.
- [ ] Use `groupby`, `agg`, `sort_values`, and `reset_index`.
- [ ] Merge related DataFrames.
- [ ] Write small reusable functions for KPI calculations.
- [ ] Create and label business charts.
- [ ] Export validated analysis tables.
- [ ] Explain errors and debug them systematically.

## Independent project understanding

- [ ] Explain why synthetic data was used.
- [ ] Explain what `generate_data.py` creates.
- [ ] Explain how `analyze_maintenance.py` validates and analyzes the data.
- [ ] Explain how `build_database.py` creates the SQLite database.
- [ ] Explain how the SQL analysis compares with the pandas analysis.
- [ ] Run `python run_project.py` successfully from a clean environment.
- [ ] Change one KPI or business rule and predict the effect before running it.
- [ ] Rebuild a simplified version without copying the original code.

## Five-minute interview walkthrough

- [ ] Business problem: 30 seconds
- [ ] Dataset and quality checks: 45 seconds
- [ ] Technical approach: 60 seconds
- [ ] Most important findings: 75 seconds
- [ ] Recommendations: 45 seconds
- [ ] Limitation and next step: 25 seconds

