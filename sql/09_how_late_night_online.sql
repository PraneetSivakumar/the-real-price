-- 09  HOW: late-night online and app purchases (22:00-05:00) - what, and how much.
-- Subscriptions are excluded because they renew automatically at ~04:30.
SELECT category,
       COUNT(*)                                 AS late_night_orders,
       ROUND(SUM(CAST(amount_gbp AS REAL)), 2)  AS spend_gbp
FROM transactions
WHERE direction = 'Debit' AND channel IN ('Online', 'App')
  AND (CAST(hour AS INTEGER) >= 22 OR CAST(hour AS INTEGER) < 5)
  AND spend_type IN ('Lifestyle', 'Leakage')
  AND category <> 'Subscriptions'
GROUP BY category
ORDER BY spend_gbp DESC;
