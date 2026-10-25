-- 01  WHAT: where does the money go? Spending by category, net of refunds, with share and hours of work.
-- Refunds (Credit rows outside Income) are subtracted from the category they belong to.
WITH net AS (
    SELECT category,
           SUM(CASE WHEN direction = 'Debit' THEN CAST(amount_gbp AS REAL) ELSE -CAST(amount_gbp AS REAL) END) AS net_spend
    FROM transactions
    WHERE category NOT IN ('Income')
    GROUP BY category
)
SELECT category,
       ROUND(net_spend, 2)                                         AS net_spend_gbp,
       ROUND(100.0 * net_spend / SUM(net_spend) OVER (), 1)        AS pct_of_total,
       ROUND(net_spend / 12.71, 1)                                 AS hours_of_work
FROM net
ORDER BY net_spend DESC;
