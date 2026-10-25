-- 04  WHEN: money in vs money out by month, and average daily spend per period.
-- October is a partial month (1-25 Oct), so compare spend per day, not monthly totals.
SELECT month,
       ROUND(SUM(CASE WHEN direction = 'Credit' AND category = 'Income' THEN CAST(amount_gbp AS REAL) ELSE 0 END), 2) AS income_gbp,
       ROUND(SUM(CASE WHEN direction = 'Debit' THEN CAST(amount_gbp AS REAL) ELSE 0 END), 2)                          AS spend_gbp,
       CASE WHEN month = '2026-10' THEN 25
            ELSE CAST(strftime('%d', date(month || '-01', '+1 month', '-1 day')) AS INTEGER) END                       AS calendar_days,
       ROUND(SUM(CASE WHEN direction = 'Debit' AND subcategory <> 'Rent' THEN CAST(amount_gbp AS REAL) ELSE 0 END)
             / CASE WHEN month = '2026-10' THEN 25
                    ELSE CAST(strftime('%d', date(month || '-01', '+1 month', '-1 day')) AS INTEGER) END, 2)            AS spend_per_day_excl_rent
FROM transactions
GROUP BY month
ORDER BY month;
