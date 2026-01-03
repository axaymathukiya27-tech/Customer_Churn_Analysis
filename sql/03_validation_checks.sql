-- 0.1 row count
SELECT COUNT(*) AS total_rows FROM combined_customer_data;

-- 0.2 basic aggregates to compare with Python results
SELECT
  COUNT(*) AS total_customers,
  SUM(Churn) AS churned_customers,
  ROUND(100*SUM(Churn)/COUNT(*),2) AS churn_rate,
  ROUND(SUM(total_revenue),2) AS total_revenue
FROM combined_customer_data;

-- 0.3 data types & null checks (important)
SELECT
  SUM(CASE WHEN customerID IS NULL THEN 1 ELSE 0 END) AS missing_customerID,
  SUM(CASE WHEN MonthlyCharges IS NULL THEN 1 ELSE 0 END) AS missing_monthly,
  SUM(CASE WHEN TotalCharges IS NULL THEN 1 ELSE 0 END) AS missing_totalcharges,
  SUM(CASE WHEN Churn IS NULL THEN 1 ELSE 0 END) AS missing_churn
FROM combined_customer_data;

-- Validation metrics for comparison
SELECT 'total_customers' AS metric, COUNT(*) AS value FROM combined_customer_data
UNION ALL
SELECT 'churned_customers', SUM(Churn) FROM combined_customer_data
UNION ALL
SELECT 'churn_rate',ROUND(100*SUM(Churn)/COUNT(*),2) FROM combined_customer_data
UNION ALL
SELECT 'sum_total_revenue', ROUND(SUM(total_revenue),2) FROM combined_customer_data;

