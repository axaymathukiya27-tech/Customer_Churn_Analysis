-- =================================================================
-- CHURN DRIVERS ANALYSIS - Comparative Metrics
-- =================================================================
-- Purpose: Identify key differences between churned and retained customers
-- Business Question: What behavioral/financial patterns distinguish churners?
-- Insights Expected: Churned customers typically have higher monthly charges 
--                    and shorter tenure
-- =================================================================

-- Compare critical metrics between churned vs retained customers
-- This analysis reveals which factors most strongly correlate with churn
WITH churned_metrics AS (
    SELECT
        'MonthlyCharges' AS metric,
        ROUND(AVG(CASE WHEN Churn=1 THEN MonthlyCharges ELSE NULL END), 2) AS avg_churned,
        ROUND(AVG(CASE WHEN Churn=0 THEN MonthlyCharges ELSE NULL END), 2) AS avg_retained,
        -- Calculate percentage difference
        ROUND(
            100 * (AVG(CASE WHEN Churn=1 THEN MonthlyCharges END) - 
                   AVG(CASE WHEN Churn=0 THEN MonthlyCharges END)) /
            AVG(CASE WHEN Churn=0 THEN MonthlyCharges END), 
        2) AS pct_difference
    FROM combined_customer_data
    
    UNION ALL
    
    SELECT
        'tenure',
        ROUND(AVG(CASE WHEN Churn=1 THEN tenure ELSE NULL END), 2),
        ROUND(AVG(CASE WHEN Churn=0 THEN tenure ELSE NULL END), 2),
        ROUND(
            100 * (AVG(CASE WHEN Churn=1 THEN tenure END) - 
                   AVG(CASE WHEN Churn=0 THEN tenure END)) /
            AVG(CASE WHEN Churn=0 THEN tenure END), 
        2)
    FROM combined_customer_data
    
    UNION ALL
    
    SELECT
        'total_revenue',
        ROUND(AVG(CASE WHEN Churn=1 THEN total_revenue ELSE NULL END), 2),
        ROUND(AVG(CASE WHEN Churn=0 THEN total_revenue ELSE NULL END), 2),
        ROUND(
            100 * (AVG(CASE WHEN Churn=1 THEN total_revenue END) - 
                   AVG(CASE WHEN Churn=0 THEN total_revenue END)) /
            AVG(CASE WHEN Churn=0 THEN total_revenue END), 
        2)
    FROM combined_customer_data
    
    UNION ALL
    
    SELECT
        'num_services',
        ROUND(AVG(CASE WHEN Churn=1 THEN num_services ELSE NULL END), 2),
        ROUND(AVG(CASE WHEN Churn=0 THEN num_services ELSE NULL END), 2),
        ROUND(
            100 * (AVG(CASE WHEN Churn=1 THEN num_services END) - 
                   AVG(CASE WHEN Churn=0 THEN num_services END)) /
            AVG(CASE WHEN Churn=0 THEN num_services END), 
        2)
    FROM combined_customer_data
)

SELECT 
    metric,
    avg_churned,
    avg_retained,
    avg_churned - avg_retained AS absolute_difference,
    pct_difference,
    -- Interpretation flag
    CASE 
        WHEN ABS(pct_difference) > 30 THEN 'High Impact'
        WHEN ABS(pct_difference) > 15 THEN 'Moderate Impact'
        ELSE 'Low Impact'
    END AS impact_level
FROM churned_metrics
ORDER BY ABS(pct_difference) DESC;

-- =================================================================
-- INTERPRETATION GUIDE
-- =================================================================
-- High percentage differences indicate strong churn predictors:
-- - tenure: Lower tenure = higher churn risk
-- - MonthlyCharges: Higher charges without proportional value = churn
-- - num_services: Fewer services = less stickiness
-- =================================================================
