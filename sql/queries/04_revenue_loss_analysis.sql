-- =================================================================
-- REVENUE LOSS ANALYSIS - Financial Impact of Customer Churn
-- =================================================================
-- Purpose: Quantify revenue losses by contract type and calculate retention ROI
-- Business Question: How much revenue are we losing to churn, and where should we invest?
-- Insights Expected: Month-to-month contracts drive majority of revenue loss
--                    Long-term contracts provide revenue stability
-- =================================================================

-- Comprehensive revenue impact analysis with forecasting
-- This calculates actual losses and projects future revenue at risk
WITH contract_churn_analysis AS (
    SELECT
        Contract,
        -- Current state metrics
        COUNT(*) AS total_customers,
        SUM(CASE WHEN Churn = 1 THEN 1 ELSE 0 END) AS churned_customers,
        SUM(CASE WHEN Churn = 0 THEN 1 ELSE 0 END) AS active_customers,
        ROUND(100.0 * SUM(Churn) / COUNT(*), 2) AS churn_rate,
        -- Revenue metrics
        ROUND(SUM(total_revenue), 2) AS total_historical_revenue,
        ROUND(SUM(CASE WHEN Churn = 1 THEN total_revenue ELSE 0 END), 2) AS lost_revenue,
        ROUND(SUM(CASE WHEN Churn = 0 THEN total_revenue ELSE 0 END), 2) AS retained_revenue,
        ROUND(AVG(CASE WHEN Churn = 1 THEN total_revenue ELSE NULL END), 2) AS avg_revenue_lost_per_churner,
        ROUND(AVG(CASE WHEN Churn = 0 THEN total_revenue ELSE NULL END), 2) AS avg_revenue_per_retained,
        -- Monthly recurring revenue (MRR) analysis
        ROUND(SUM(CASE WHEN Churn = 0 THEN MonthlyCharges ELSE 0 END), 2) AS current_mrr,
        ROUND(SUM(CASE WHEN Churn = 1 THEN MonthlyCharges ELSE 0 END), 2) AS lost_mrr,
        ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charge
    FROM combined_customer_data
    GROUP BY Contract
),
revenue_projections AS (
    SELECT
        *,
        -- Calculate customer lifetime value (CLV) for each contract type
        ROUND(avg_monthly_charge * (12 / (churn_rate / 100)), 2) AS estimated_clv,
        -- Project annual revenue loss if churn continues at current rate
        ROUND(lost_mrr * 12, 2) AS projected_annual_loss,
        -- Calculate potential recovery scenarios
        ROUND(lost_revenue * 0.25, 2) AS revenue_recovery_25pct,  -- Conservative scenario
        ROUND(lost_revenue * 0.50, 2) AS revenue_recovery_50pct,  -- Moderate scenario
        ROUND(lost_revenue * 0.75, 2) AS revenue_recovery_75pct,  -- Aggressive scenario
        -- Revenue concentration risk
        ROUND(100.0 * lost_revenue / SUM(lost_revenue) OVER(), 2) AS pct_of_total_loss
    FROM contract_churn_analysis
)

SELECT 
    Contract,
    total_customers,
    churned_customers,
    active_customers,
    churn_rate,
    -- Historical revenue
    lost_revenue,
    retained_revenue,
    total_historical_revenue,
    avg_revenue_lost_per_churner,
    -- Current & projected revenue
    current_mrr,
    lost_mrr,
    projected_annual_loss,
    estimated_clv,
    -- Recovery scenarios
    revenue_recovery_25pct AS conservative_recovery,
    revenue_recovery_50pct AS moderate_recovery,
    revenue_recovery_75pct AS aggressive_recovery,
    pct_of_total_loss,
    -- ROI calculation: If we spend 10% of lost revenue on retention
    ROUND(revenue_recovery_50pct - (lost_revenue * 0.10), 2) AS net_gain_50pct_retention,
    -- Recommended retention budget allocation
    ROUND(pct_of_total_loss / 100 * 50000, 2) AS suggested_retention_budget,
    -- Business insights
    CASE 
        WHEN churn_rate > 40 THEN 'CRITICAL: Redesign contract value proposition'
        WHEN churn_rate > 25 THEN 'HIGH PRIORITY: Implement aggressive retention'
        WHEN churn_rate < 10 THEN 'SUCCESS: Current strategy working well'
        ELSE 'MODERATE: Standard retention tactics'
    END AS strategic_priority,
    -- Action recommendations
    CASE 
        WHEN Contract = 'Month-to-month' THEN 'Incentivize contract upgrades with loyalty rewards'
        WHEN Contract = 'One year' THEN 'Add early renewal bonuses to prevent churn'
        WHEN Contract = 'Two year' THEN 'Focus on satisfaction surveys and upsell opportunities'
        ELSE 'Review contract terms'
    END AS recommended_action
FROM revenue_projections
ORDER BY lost_revenue DESC;

-- =================================================================
-- SUMMARY METRICS - Executive Dashboard View
-- =================================================================
SELECT 
    ROUND(SUM(CASE WHEN Churn = 1 THEN total_revenue ELSE 0 END), 2) AS total_revenue_lost,
    ROUND(SUM(CASE WHEN Churn = 1 THEN MonthlyCharges ELSE 0 END) * 12, 2) AS annual_mrr_at_risk,
    COUNT(CASE WHEN Churn = 1 THEN 1 END) AS total_customers_churned,
    ROUND(AVG(CASE WHEN Churn = 1 THEN total_revenue END), 2) AS avg_lifetime_value_lost,
    -- If we reduce churn by 30%, projected revenue gain
    ROUND(SUM(CASE WHEN Churn = 1 THEN total_revenue ELSE 0 END) * 0.30, 2) AS revenue_opportunity_30pct_reduction
FROM combined_customer_data;

-- =================================================================
-- INTERPRETATION GUIDE
-- =================================================================
-- Projected Annual Loss: Annualized MRR loss if churn continues
-- Estimated CLV: Average customer lifetime value by contract type
-- Recovery Scenarios: Expected revenue gain from churn reduction programs
-- Net Gain: ROI after subtracting retention program costs
--
-- Decision Framework:
-- - Allocate retention budget proportional to % of total loss
-- - Focus on contract types with highest churn rates first
-- - Target 50% churn reduction as realistic goal (typically achievable)
-- - Expected ROI: $5 saved for every $1 spent on retention
-- =================================================================
