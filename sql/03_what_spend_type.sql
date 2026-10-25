-- 03  WHAT: how much is Essential, Investment, Lifestyle or Leakage?
SELECT spend_type,
       COUNT(*)                                                                 AS transactions,
       ROUND(SUM(CAST(amount_gbp AS REAL)), 2)                                  AS spend_gbp,
       ROUND(100.0 * SUM(CAST(amount_gbp AS REAL)) / SUM(SUM(CAST(amount_gbp AS REAL))) OVER (), 1) AS pct
FROM transactions
WHERE direction = 'Debit'
GROUP BY spend_type
ORDER BY spend_gbp DESC;
