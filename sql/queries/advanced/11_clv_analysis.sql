-- =================================================================
-- CUSTOMER LIFETIME VALUE (CLV) ANALYSIS
-- =================================================================
-- Purpose: Calculate expected customer lifetime value factoring in churn probability
-- Business Use: Prioritize retention efforts by customer value
-- Formula: CLV = (Avg Monthly Revenue × Avg Customer Lifespan) / (1 + Discount Rate)
-- =================================================================

-- Step 1: Calculate average customer metrics by segment
WITH customer_metrics AS (
    SELECT 
        customerID,
        tenure,
        MonthlyCharges,
        total_revenue,
        Contract,
        num_services,
        Churn,
        -- Calculate expected remaining lifetime (months)
        CASE 
            WHEN tenure < 12 THEN 24  -- New customers: assume 24 month potential
            WHEN tenure BETWEEN 12 AND 24 THEN 36  -- Established: 36 months
            WHEN tenure > 24 THEN 48  -- Loyal: 48 months
        END AS expected_lifetime_months,
        -- Segment-specific churn probability
        CASE 
            WHEN Contract = 'Month-to-month' THEN 0.427
            WHEN Contract = 'One year' THEN 0.113
            WHEN Contract = 'Two year' THEN 0.028
        END AS churn_probability
    FROM combined_customer_data
    WHERE Churn = 0  -- Only active customers
),

-- Step 2: Calculate CLV per customer
clv_calculation AS (
    SELECT 
        customerID,
        MonthlyCharges,
        tenure,
        Contract,
        num_services,
        expected_lifetime_months,
        churn_probability,
        -- CLV = Monthly Revenue × Expected Lifetime × Retention Probability
        ROUND(
            MonthlyCharges * expected_lifetime_months * (1 - churn_probability),
            2
        ) AS estimated_clv,
        -- Simple CLV (without churn adjustment)
        ROUND(MonthlyCharges * expected_lifetime_months, 2) AS simple_clv,
        -- Lifetime value at risk (if customer churns)
        ROUND(MonthlyCharges * expected_lifetime_months * churn_probability, 2) AS value_at_risk
    FROM customer_metrics
)

-- Final output: Customer-level CLV with rankings
SELECT 
    customerID,
    MonthlyCharges,
    tenure,
    Contract,
    num_services,
    estimated_clv,
    value_at_risk,
    -- Rank customers by CLV for prioritization
    ROW_NUMBER() OVER (ORDER BY estimated_clv DESC) AS clv_rank,
    -- Categorize CLV tiers
    CASE 
        WHEN estimated_clv > 5000 THEN 'Premium'
        WHEN estimated_clv BETWEEN 2500 AND 5000 THEN 'High Value'
        WHEN estimated_clv BETWEEN 1000 AND 2500 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS clv_tier
FROM clv_calculation
ORDER BY estimated_clv DESC;

-- Export for Power BI
SELECT * FROM clv_calculation
INTO OUTFILE '/path/to/exports/query_results/clv_analysis_results.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
