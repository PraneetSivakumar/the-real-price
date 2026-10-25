-- 02  WHAT: who gets my money? Top 10 merchants (excluding rent and income) by spend and visit count.
SELECT merchant,
       COUNT(*)                                   AS transactions,
       ROUND(SUM(CAST(amount_gbp AS REAL)), 2)    AS spend_gbp,
       ROUND(AVG(CAST(amount_gbp AS REAL)), 2)    AS avg_basket_gbp
FROM transactions
WHERE direction = 'Debit' AND subcategory <> 'Rent'
GROUP BY merchant
ORDER BY spend_gbp DESC
LIMIT 10;
