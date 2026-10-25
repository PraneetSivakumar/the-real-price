-- 07  WHY: do shift days trigger takeaways? Takeaway orders and spend on shift vs non-shift days, and by hour.
SELECT CASE WHEN shift_day = 'True' THEN 'Shift day' ELSE 'Non-shift day' END AS day_type,
       COUNT(*)                                 AS takeaway_orders,
       ROUND(SUM(CAST(amount_gbp AS REAL)), 2)  AS takeaway_spend_gbp,
       SUM(CASE WHEN CAST(hour AS INTEGER) >= 21 OR CAST(hour AS INTEGER) < 5 THEN 1 ELSE 0 END) AS orders_after_9pm
FROM transactions
WHERE subcategory = 'Takeaway delivery'
GROUP BY day_type;
