-- Adds quarterly TRx goals. Run from the repo ROOT:
--   psql -U postgres -h localhost -d pharma_db -f sql/02_add_quota.sql
SET search_path = pharma;
DROP TABLE IF EXISTS fact_quota;
CREATE TABLE fact_quota (
  quota_id INT PRIMARY KEY,
  territory_id INT NOT NULL REFERENCES dim_territory,
  product_id INT NOT NULL REFERENCES dim_product,
  quarter_start_date DATE NOT NULL REFERENCES dim_date,
  quarter_label TEXT,
  trx_goal INT NOT NULL,
  UNIQUE (territory_id, product_id, quarter_start_date));
\copy fact_quota FROM 'data/fact_quota.csv' CSV HEADER
SELECT count(*) AS quota_rows FROM fact_quota;   -- expect 720
