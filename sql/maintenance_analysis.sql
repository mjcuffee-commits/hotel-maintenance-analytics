-- Hotel Maintenance Operations Analytics
-- Database: SQLite | Table: work_orders
-- Run `python src/build_database.py` before using these queries.

-- 1. Headline operating metrics
SELECT
    COUNT(*) AS total_work_orders,
    ROUND(SUM(total_cost), 2) AS total_maintenance_cost,
    ROUND(AVG(response_minutes), 1) AS average_response_minutes,
    ROUND(100.0 * AVG(sla_met), 1) AS sla_compliance_pct,
    ROUND(100.0 * AVG(repeat_within_30_days), 1) AS repeat_repair_pct,
    ROUND(AVG(downtime_hours), 2) AS average_downtime_hours
FROM work_orders;


-- 2. Identify the systems driving work volume, cost, and downtime
SELECT
    system_type,
    COUNT(*) AS work_orders,
    ROUND(SUM(total_cost), 2) AS total_cost,
    ROUND(AVG(total_cost), 2) AS average_cost,
    ROUND(AVG(downtime_hours), 2) AS average_downtime_hours,
    ROUND(100.0 * AVG(repeat_within_30_days), 1) AS repeat_rate_pct
FROM work_orders
GROUP BY system_type
ORDER BY total_cost DESC;


-- 3. Compare response performance across engineering shifts
SELECT
    shift,
    COUNT(*) AS work_orders,
    ROUND(AVG(response_minutes), 1) AS average_response_minutes,
    ROUND(100.0 * AVG(sla_met), 1) AS sla_compliance_pct,
    SUM(guest_impact) AS guest_impact_work_orders
FROM work_orders
GROUP BY shift
ORDER BY sla_compliance_pct DESC;


-- 4. Compare preventive and corrective maintenance
SELECT
    maintenance_type,
    COUNT(*) AS work_orders,
    ROUND(AVG(total_cost), 2) AS average_cost,
    ROUND(AVG(downtime_hours), 2) AS average_downtime_hours,
    ROUND(100.0 * AVG(repeat_within_30_days), 1) AS repeat_rate_pct
FROM work_orders
GROUP BY maintenance_type
ORDER BY average_cost DESC;


-- 5. Measure repeat-repair risk by asset age
WITH age_bands AS (
    SELECT
        CASE
            WHEN asset_age_years <= 5 THEN '1-5 years'
            WHEN asset_age_years <= 10 THEN '6-10 years'
            WHEN asset_age_years <= 15 THEN '11-15 years'
            ELSE '16+ years'
        END AS asset_age_group,
        CASE
            WHEN asset_age_years <= 5 THEN 1
            WHEN asset_age_years <= 10 THEN 2
            WHEN asset_age_years <= 15 THEN 3
            ELSE 4
        END AS age_sort,
        total_cost,
        downtime_hours,
        repeat_within_30_days
    FROM work_orders
)
SELECT
    asset_age_group,
    COUNT(*) AS work_orders,
    ROUND(AVG(total_cost), 2) AS average_cost,
    ROUND(AVG(downtime_hours), 2) AS average_downtime_hours,
    ROUND(100.0 * AVG(repeat_within_30_days), 1) AS repeat_rate_pct
FROM age_bands
GROUP BY asset_age_group, age_sort
ORDER BY age_sort;


-- 6. Find the highest-impact recurring issue categories
SELECT
    system_type,
    issue_type,
    COUNT(*) AS work_orders,
    SUM(guest_impact) AS guest_impact_work_orders,
    ROUND(SUM(total_cost), 2) AS total_cost,
    ROUND(100.0 * AVG(repeat_within_30_days), 1) AS repeat_rate_pct
FROM work_orders
WHERE maintenance_type = 'Corrective'
GROUP BY system_type, issue_type
HAVING COUNT(*) >= 10
ORDER BY guest_impact_work_orders DESC, total_cost DESC
LIMIT 10;


-- 7. Monthly trend for a management scorecard
SELECT
    SUBSTR(opened_at, 1, 7) AS opened_month,
    COUNT(*) AS work_orders,
    ROUND(SUM(total_cost), 2) AS total_cost,
    ROUND(100.0 * AVG(sla_met), 1) AS sla_compliance_pct
FROM work_orders
GROUP BY opened_month
ORDER BY opened_month;
