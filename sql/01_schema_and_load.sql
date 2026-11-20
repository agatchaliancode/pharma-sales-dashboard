-- Pharma Sales Dashboard - sample data (synthetic).
--   psql -d <your_db> -f sql/01_schema_and_load.sql
-- Run from the repo ROOT so the data/ paths resolve.

DROP SCHEMA IF EXISTS pharma CASCADE;
CREATE SCHEMA pharma;
SET search_path = pharma;

CREATE TABLE dim_date (
  date_key DATE PRIMARY KEY, week_start_date DATE, week_ending_date DATE,
  year INT, quarter INT, quarter_label TEXT, quarter_start_date DATE,
  month_num INT, month_name TEXT, month_start_date DATE, year_month TEXT,
  day_name TEXT, is_weekend BOOLEAN);

CREATE TABLE dim_territory (
  territory_id INT PRIMARY KEY, territory_code TEXT, territory_name TEXT,
  region_id INT, region_name TEXT);

CREATE TABLE dim_product (
  product_id INT PRIMARY KEY, product_name TEXT, therapeutic_area TEXT, launch_date DATE);

CREATE TABLE dim_rep (
  rep_id INT PRIMARY KEY, rep_name TEXT, territory_id INT REFERENCES dim_territory,
  hire_date DATE, job_title TEXT);

CREATE TABLE dim_hcp (
  hcp_id INT PRIMARY KEY, npi_number TEXT, hcp_name TEXT, credential TEXT,
  specialty TEXT, city TEXT, priority_tier TEXT CHECK (priority_tier IN ('A','B','C','NP')),
  territory_id INT REFERENCES dim_territory);

CREATE TABLE fact_trx_weekly (          -- weekly TRx; zero-TRx weeks are not stored
  week_ending_date DATE REFERENCES dim_date, hcp_id INT REFERENCES dim_hcp,
  product_id INT REFERENCES dim_product, trx INT, data_status TEXT,
  PRIMARY KEY (week_ending_date, hcp_id, product_id));

CREATE TABLE fact_calls (
  call_id INT PRIMARY KEY, call_date DATE REFERENCES dim_date, hcp_id INT REFERENCES dim_hcp,
  rep_id INT REFERENCES dim_rep, product_id INT REFERENCES dim_product, call_type TEXT);

CREATE TABLE data_refresh (dataset_name TEXT PRIMARY KEY, latest_data_date DATE);

\copy dim_date        FROM 'data/dim_date.csv'        CSV HEADER
\copy dim_territory   FROM 'data/dim_territory.csv'   CSV HEADER
\copy dim_product     FROM 'data/dim_product.csv'     CSV HEADER
\copy dim_rep         FROM 'data/dim_rep.csv'         CSV HEADER
\copy dim_hcp         FROM 'data/dim_hcp.csv'         CSV HEADER
\copy fact_trx_weekly FROM 'data/fact_trx_weekly.csv' CSV HEADER
\copy fact_calls      FROM 'data/fact_calls.csv'      CSV HEADER
\copy data_refresh    FROM 'data/data_refresh.csv'    CSV HEADER

CREATE INDEX ix_trx_hcp   ON fact_trx_weekly (hcp_id);
CREATE INDEX ix_calls_hcp ON fact_calls (hcp_id, call_date);
CREATE INDEX ix_hcp_terr  ON dim_hcp (territory_id);
ANALYZE;

-- Row-count check: expect ~1,963 HCPs, ~106,861 TRx rows, ~88,279 calls
SELECT 'dim_hcp' t, count(*) FROM dim_hcp UNION ALL
SELECT 'fact_trx_weekly', count(*) FROM fact_trx_weekly UNION ALL
SELECT 'fact_calls', count(*) FROM fact_calls;

-- Optional validation view: HCP 13-week classification (compare against your DAX results)
CREATE VIEW vw_hcp_13wk_check AS
WITH latest AS (SELECT max(week_ending_date) AS wk FROM fact_trx_weekly),
agg AS (
  SELECT h.hcp_id, h.hcp_name, h.city, h.specialty, h.priority_tier, h.territory_id,
    COALESCE(sum(f.trx) FILTER (WHERE f.week_ending_date >  l.wk - 91), 0)                              AS trx_curr_13,
    COALESCE(sum(f.trx) FILTER (WHERE f.week_ending_date <= l.wk - 91 AND f.week_ending_date > l.wk - 182), 0) AS trx_prior_13,
    COALESCE(sum(f.trx) FILTER (WHERE f.week_ending_date <= l.wk - 91), 0)                              AS trx_lifetime_before
  FROM dim_hcp h CROSS JOIN latest l LEFT JOIN fact_trx_weekly f ON f.hcp_id = h.hcp_id
  GROUP BY h.hcp_id, h.hcp_name, h.city, h.specialty, h.priority_tier, h.territory_id)
SELECT *, trx_curr_13 - trx_prior_13 AS trx_chg_13,
  (trx_curr_13 > 0 AND trx_lifetime_before = 0) AS is_new_writer
FROM agg;
