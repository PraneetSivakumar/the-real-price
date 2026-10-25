-- 08  HOW: does the way I pay change what I spend? Spend by payment method, and the top-up premium.
SELECT payment_method,
       COUNT(*)                                 AS transactions,
       ROUND(SUM(CAST(amount_gbp AS REAL)), 2)  AS spend_gbp,
       ROUND(AVG(CAST(amount_gbp AS REAL)), 2)  AS avg_gbp
FROM transactions
WHERE direction = 'Debit' AND spend_type IN ('Lifestyle', 'Leakage')
GROUP BY payment_method
ORDER BY spend_gbp DESC;

-- Top-up shops vs weekly shops: how many trips, and what share of grocery money goes on top-ups?
SELECT subcategory,
       COUNT(*)                                                                         AS trips,
       ROUND(SUM(CAST(amount_gbp AS REAL)), 2)                                          AS spend_gbp,
       ROUND(AVG(CAST(amount_gbp AS REAL)), 2)                                          AS avg_trip_gbp,
       ROUND(100.0 * SUM(CAST(amount_gbp AS REAL)) / SUM(SUM(CAST(amount_gbp AS REAL))) OVER (), 1) AS pct_of_groceries
FROM transactions
WHERE category = 'Groceries'
GROUP BY subcategory;
