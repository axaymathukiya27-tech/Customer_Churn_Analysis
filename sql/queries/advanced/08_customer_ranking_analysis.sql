-- =================================================================
-- CUSTOMER VALUE RANKING WITH WINDOW FUNCTIONS
-- =================================================================
-- Purpose: Rank customers by multiple dimensions for targeted campaigns
-- Techniques Used: ROW_NUMBER, RANK, DENSE_RANK, NTILE, PERCENT_RANK
-- Business Use: Identify VIP customers, at-risk high-value accounts
-- =================================================================

WITH customer_rankings AS (
    SELECT
        customerID,
        tenure,
        MonthlyCharges,
        total_revenue,
        num_services,
        Contract,
        Churn,
        
        -- Rank by total revenue (1 = highest revenue)
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
        
        -- Rank by monthly charges
        RANK() OVER (ORDER BY MonthlyCharges DESC) AS monthly_charge_rank,
        
        -- Percentile ranking (0-1 scale)
        PERCENT_RANK() OVER (ORDER BY total_revenue) AS revenue_percentile,
        
        -- Divide customers into 10 deciles by revenue
        NTILE(10) OVER (ORDER BY total_revenue DESC) AS revenue_decile,
        
        -- Rank within contract type
        ROW_NUMBER() OVER (
            PARTITION BY Contract 
            ORDER BY total_revenue DESC
        ) AS rank_within_contract,
        
        -- Calculate running total of revenue
        SUM(total_revenue) OVER (
            ORDER BY total_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue,
        
        -- Moving average of monthly charges (3-customer window)
        AVG(MonthlyCharges) OVER (
            ORDER BY customerID
            ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
        ) AS moving_avg_charges
        
    FROM combined_customer_data
    WHERE Churn = 0  -- Active customers only
)

SELECT
    customerID,
    tenure,
    MonthlyCharges,
    total_revenue,
    revenue_rank,
    revenue_decile,
    ROUND(revenue_percentile * 100, 2) AS revenue_percentile_pct,
    rank_within_contract,
    
    -- Pareto Analysis: Identify top 20% revenue generators
    CASE 
        WHEN revenue_percentile >= 0.80 THEN 'Top 20% (VIP)'
        WHEN revenue_percentile >= 0.50 THEN 'Middle 30%'
        ELSE 'Bottom 50%'
    END AS customer_tier,
    
    -- Flag high-risk VIP customers
    CASE
        WHEN revenue_decile <= 3 AND tenure < 12 THEN 'VIP at Risk'
        WHEN revenue_decile <= 3 THEN 'VIP Secure'
        WHEN revenue_decile >= 8 THEN 'Low Value'
        ELSE 'Standard'
    END AS risk_segment
    
FROM customer_rankings
WHERE revenue_rank <= 500  -- Top 500 customers
ORDER BY revenue_rank;
