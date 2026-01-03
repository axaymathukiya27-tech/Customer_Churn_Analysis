-- =================================================================
-- SERVICE ADOPTION TIERS ANALYSIS
-- =================================================================
-- Purpose: Classify customers into service adoption tiers
-- Business Use: Identify upsell opportunities and tier-based churn risk
-- =================================================================

WITH service_tiers AS (
    SELECT
        customerID,
        num_services,
        tenure,
        MonthlyCharges,
        total_revenue,
        Contract,
        Churn,
        -- Create service adoption tiers
        CASE
            WHEN num_services = 0 THEN 'No Services'
            WHEN num_services = 1 THEN 'Single Service'
            WHEN num_services BETWEEN 2 AND 3 THEN 'Basic Bundle'
            WHEN num_services BETWEEN 4 AND 5 THEN 'Standard Bundle'
            WHEN num_services >= 6 THEN 'Premium Bundle'
        END AS service_tier,
        CASE
            WHEN num_services = 0 THEN 1
            WHEN num_services = 1 THEN 2
            WHEN num_services BETWEEN 2 AND 3 THEN 3
            WHEN num_services BETWEEN 4 AND 5 THEN 4
            WHEN num_services >= 6 THEN 5
        END AS tier_rank
    FROM combined_customer_data
)

SELECT
    service_tier,
    tier_rank,
    COUNT(*) AS customers_in_tier,
    ROUND(AVG(num_services), 2) AS avg_services,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_revenue,
    ROUND(AVG(total_revenue), 2) AS avg_lifetime_value,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    ROUND(100.0 * SUM(Churn) / COUNT(*), 2) AS churn_rate,
    ROUND(100.0 * SUM(CASE WHEN Churn = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS retention_rate,
    -- Calculate revenue opportunity if all churned customers were retained
    ROUND(SUM(CASE WHEN Churn = 1 THEN total_revenue ELSE 0 END), 2) AS lost_revenue
FROM service_tiers
GROUP BY service_tier, tier_rank
ORDER BY tier_rank;
