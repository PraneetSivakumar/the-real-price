-- 10  SOLUTION: subscription audit. Any merchant charging on 3+ different months is treated as recurring.
-- Flag the ones mapped as Leakage (zombie / duplicate) and what they cost per year at the current price.
WITH recurring AS (
    SELECT merchant,
           COUNT(DISTINCT month)                        AS months_charged,
           ROUND(SUM(CAST(amount_gbp AS REAL)), 2)      AS paid_so_far_gbp,
           ROUND(MAX(CAST(amount_gbp AS REAL)), 2)      AS monthly_price_gbp,
           MAX(spend_type)                              AS spend_type
    FROM transactions
    WHERE category = 'Subscriptions' AND direction = 'Debit'
    GROUP BY merchant
    HAVING COUNT(DISTINCT month) >= 3
)
SELECT merchant, months_charged, monthly_price_gbp, paid_so_far_gbp,
       ROUND(monthly_price_gbp * 12, 2)                 AS cost_per_year_gbp,
       CASE WHEN spend_type = 'Leakage' THEN 'CANCEL' ELSE 'keep / review' END AS action
FROM recurring
ORDER BY action, cost_per_year_gbp DESC;
