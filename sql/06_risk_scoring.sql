-- Basic in-SQL scoring rules

CREATE OR REPLACE VIEW v_risk_score AS
SELECT customerID,
  (0.4 * (CASE WHEN month_to_month=1 THEN 1 ELSE 0 END) +
   0.25 * (CASE WHEN tenure < 6 THEN 1 ELSE 0 END) +
   0.2 * (CASE WHEN MonthlyCharges > (SELECT AVG(MonthlyCharges) FROM combined_customer_data) THEN 1 ELSE 0 END) +
   0.15 * (CASE WHEN charge_ratio > 1 THEN 1 ELSE 0 END)
  ) AS risk_score
FROM (
  SELECT customerID, MonthlyCharges, tenure, charge_ratio,
         CASE WHEN Contract='Month-to-month' THEN 1 ELSE 0 END AS month_to_month
  FROM combined_customer_data
) t;

-- Get top 100 high-risk customers
SELECT customerID, risk_score
FROM v_risk_score
ORDER BY risk_score DESC
LIMIT 100;
