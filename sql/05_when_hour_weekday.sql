-- 05  WHEN: which time band and weekday cost the most (discretionary spending only)?
-- Subscriptions are excluded: they auto-renew at ~04:30, which is not a choice made at that hour.
SELECT time_band,
       COUNT(*)                                 AS transactions,
       ROUND(SUM(CAST(amount_gbp AS REAL)), 2)  AS spend_gbp
FROM transactions
WHERE direction = 'Debit' AND spend_type IN ('Lifestyle', 'Leakage') AND category <> 'Subscriptions'
GROUP BY time_band
ORDER BY spend_gbp DESC;

SELECT weekday,
       COUNT(*)                                 AS transactions,
       ROUND(SUM(CAST(amount_gbp AS REAL)), 2)  AS spend_gbp
FROM transactions
WHERE direction = 'Debit' AND spend_type IN ('Lifestyle', 'Leakage') AND category <> 'Subscriptions'
GROUP BY weekday
ORDER BY spend_gbp DESC;
