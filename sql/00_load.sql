-- 00_load.sql  -  Load the enriched data into a local SQLite database.
-- Run from the project root:  sqlite3 spending.db < sql/00_load.sql
DROP TABLE IF EXISTS transactions;
.mode csv
.import data/processed/transactions_enriched.csv transactions
-- Quick check: how many rows, and what date range?
.mode column
.headers on
SELECT COUNT(*) AS rows_loaded, MIN(date) AS first_day, MAX(date) AS last_day FROM transactions;
