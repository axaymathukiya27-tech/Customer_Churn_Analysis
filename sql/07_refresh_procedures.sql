-- Automate refresh & scheduling

DELIMITER //
CREATE PROCEDURE refresh_summaries()
BEGIN
  DROP TABLE IF EXISTS summary_churn_by_segment;
  CREATE TABLE summary_churn_by_segment AS
  SELECT tenure_group, charge_category, Contract, 
         COUNT(*) AS customers,
         SUM(Churn) AS churned,
         ROUND(100 * SUM(Churn)/COUNT(*),2) AS churn_rate,
         ROUND(AVG(total_revenue),2) AS avg_revenue
  FROM combined_customer_data
  GROUP BY tenure_group, charge_category, Contract;
END //
DELIMITER ;

-- Enable event scheduler 
-- SET GLOBAL event_scheduler = ON;

-- Create daily refresh event 
-- CREATE EVENT IF NOT EXISTS ev_refresh_summaries
-- ON SCHEDULE EVERY 1 DAY
-- DO CALL refresh_summaries();
