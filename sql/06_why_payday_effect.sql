-- 06  WHY: the payday effect. Average discretionary spend per calendar day, by days since payday.
-- Step 1 builds one row per calendar day (so days with no spending count as zero).
-- Subscriptions are excluded: they renew automatically, whatever the payday.
WITH RECURSIVE days(d) AS (
    SELECT '2026-01-09'
    UNION ALL SELECT date(d, '+1 day') FROM days WHERE d < '2026-10-25'
),
paydays AS (
    SELECT DISTINCT date AS pd FROM transactions WHERE direction = 'Credit' AND category = 'Income'
),
day_bucket AS (
    SELECT d,
           CAST(julianday(d) - julianday((SELECT MAX(pd) FROM paydays WHERE pd <= d)) AS INTEGER) AS dsp
    FROM days
),
daily AS (
    SELECT date, SUM(CAST(amount_gbp AS REAL)) AS spend
    FROM transactions
    WHERE direction = 'Debit' AND spend_type IN ('Lifestyle', 'Leakage') AND category <> 'Subscriptions'
    GROUP BY date
)
SELECT CASE WHEN dsp <= 3 THEN '0-3 days after payday'
            WHEN dsp <= 10 THEN '4-10 days'
            ELSE '11+ days' END                        AS payday_window,
       COUNT(*)                                        AS calendar_days,
       ROUND(AVG(COALESCE(daily.spend, 0)), 2)         AS avg_discretionary_per_day
FROM day_bucket
LEFT JOIN daily ON daily.date = day_bucket.d
GROUP BY payday_window
ORDER BY MIN(dsp);
