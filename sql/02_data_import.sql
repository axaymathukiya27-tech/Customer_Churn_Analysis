-- =================================================================
-- VERIFIED DATA IMPORT - WINDOWS MYSQL WORKBENCH
-- =================================================================
-- Status: ✓ Successfully tested on MySQL 8.0 / Windows 10
-- Method: Table Data Import Wizard (recommended for Windows)
-- Alternative: LOAD DATA LOCAL INFILE (requires configuration)
-- =================================================================

-- METHOD 1: MySQL Workbench GUI (RECOMMENDED for Windows)
-- ----------------------------------------------------
-- 1. Right-click 'combined_customer_data' table in Navigator panel
-- 2. Select "Table Data Import Wizard"
-- 3. Browse to: customer_churn_master.csv
-- 4. Configure import:
--    - Field separator: , (comma)
--    - Line separator: \n (newline)
--    - Enclose strings: " (double quote)
-- 5. Map CSV columns to table columns (auto-detected)
-- 6. Click "Next" → "Next" → "Finish"
-- 7. Verify import with validation query below

-- Verification Query
SELECT
    COUNT(*) AS total_rows_imported,
    COUNT(DISTINCT customerID) AS unique_customers,
    SUM(Churn) AS churned_customers,
    ROUND(100*SUM(Churn)/COUNT(*), 2) AS churn_rate_pct,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    MIN(tenure) AS min_tenure,
    MAX(tenure) AS max_tenure
FROM combined_customer_data;

-- Expected Output:
-- total_rows_imported: 7,286
-- unique_customers: 7,286
-- churned_customers: 1,971
-- churn_rate_pct: 27.05%
-- total_revenue: $15,951,746.58

-- =================================================================
-- METHOD 2: Command Line Import (Alternative)
-- =================================================================
-- If using command line, first enable local file loading:
-- SET GLOBAL local_infile = 1;

-- Then run (update path to your CSV location):
LOAD DATA LOCAL INFILE 'C:/Users/YourName/Projects/customer-churn/data/sql_exports/combined_customer_data.csv'
INTO TABLE combined_customer_data
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
