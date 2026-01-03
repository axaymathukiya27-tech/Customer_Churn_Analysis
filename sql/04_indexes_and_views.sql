
-- Add indexes to speed up analytic queries
CREATE INDEX idx_tenure ON combined_customer_data(tenure);
CREATE INDEX idx_churn ON combined_customer_data(Churn);
CREATE INDEX idx_contract ON combined_customer_data(Contract);
CREATE INDEX idx_tenure_group ON combined_customer_data(tenure_group);
CREATE INDEX idx_payment ON combined_customer_data(PaymentMethod);
CREATE INDEX idx_num_services ON combined_customer_data(num_services);

-- Create concise view used by dashboards/queries
CREATE OR REPLACE VIEW v_customer_core AS
SELECT
  customerID, gender, SeniorCitizen, Partner, Dependents,
  tenure, tenure_group, PhoneService, MultipleLines, InternetService,
  Contract, PaymentMethod, PaperlessBilling, paperless_billing_binary,
  MonthlyCharges, TotalCharges, total_revenue, charge_ratio, charge_category,
  num_services, is_new_customer, is_long_term, family_size, Churn
FROM combined_customer_data;

-- Create materialized summary table (refresh as needed)
DROP TABLE IF EXISTS summary_churn_by_segment;
CREATE TABLE summary_churn_by_segment AS
SELECT
  tenure_group, charge_category, Contract,
  COUNT(*) AS customers,
  SUM(Churn) AS churned,
  ROUND(100 * SUM(Churn)/COUNT(*),2) AS churn_rate,
  ROUND(AVG(total_revenue),2) AS avg_revenue
FROM combined_customer_data
GROUP BY tenure_group, charge_category, Contract;

-- Export summary table
SELECT * FROM summary_churn_by_segment;
