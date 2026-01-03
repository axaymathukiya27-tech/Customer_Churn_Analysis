-- Feature engineering for modeling & segmentation

DROP TABLE IF EXISTS features_for_model;
CREATE TABLE features_for_model AS
SELECT
  customerID,
  SeniorCitizen,
  CASE WHEN gender='Male' THEN 1 ELSE 0 END AS male_flag,
  Partner, Dependents,
  tenure,
  MonthlyCharges,
  TotalCharges,
  total_revenue,
  charge_ratio,
  num_services,
  CASE WHEN Contract='Month-to-month' THEN 1 ELSE 0 END AS month_to_month,
  paperless_billing_binary,
  is_new_customer,
  family_size,
  Churn
FROM combined_customer_data;

-- Export features table
SELECT * FROM features_for_model;
