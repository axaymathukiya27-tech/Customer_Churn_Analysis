-- =================================================================
-- SEGMENT RISK ANALYSIS - Multi-Dimensional Churn Assessment
-- =================================================================
-- Purpose: Identify customer segments with highest churn risk and revenue exposure
-- Business Question: Which customer segments should we prioritize for retention efforts?
-- Insights Expected: New customers with high charges show elevated churn rates
--                    Long-term customers provide stable revenue with low churn
-- =================================================================

-- Cross-segment analysis combining tenure and spending patterns
-- This reveals which combinations of customer characteristics drive churn
WITH segment_metrics AS (
    SELECT
        tenure_group,
        charge_category,
        COUNT(*) AS total_customers,
        SUM(Churn) AS churned_customers,
        SUM(CASE WHEN Churn = 0 THEN 1 ELSE 0 END) AS retained_customers,
        ROUND(100.0 * SUM(Churn) / COUNT(*), 2) AS churn_rate,
        ROUND(AVG(total_revenue), 2) AS avg_revenue_per_customer,
        ROUND(SUM(total_revenue), 2) AS total_segment_revenue,
        -- Calculate revenue at risk from this segment
        ROUND(SUM(CASE WHEN Churn = 1 THEN total_revenue ELSE 0 END), 2) AS lost_revenue,
        ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charge,
        ROUND(AVG(tenure), 1) AS avg_tenure_months
    FROM combined_customer_data
    GROUP BY tenure_group, charge_category
),
segment_risk AS (
    SELECT
        *,
        -- Calculate potential revenue if we could reduce churn by 50%
        ROUND(lost_revenue * 0.5, 2) AS recoverable_revenue,
        -- Risk score: combination of churn rate and revenue exposure
        ROUND((churn_rate / 100) * (total_segment_revenue / 1000), 2) AS risk_score,
        -- Classify segments by priority
        CASE 
            WHEN churn_rate > 50 AND total_segment_revenue > 50000 THEN 'Critical Priority'
            WHEN churn_rate > 40 OR total_segment_revenue > 100000 THEN 'High Priority'
            WHEN churn_rate > 25 THEN 'Medium Priority'
            ELSE 'Monitor'
        END AS priority_level
    FROM segment_metrics
)

SELECT 
    tenure_group,
    charge_category,
    total_customers,
    churned_customers,
    retained_customers,
    churn_rate,
    avg_revenue_per_customer,
    total_segment_revenue,
    lost_revenue,
    recoverable_revenue,
    avg_monthly_charge,
    avg_tenure_months,
    risk_score,
    priority_level,
    -- Add segment insights
    CASE 
        WHEN churn_rate > 60 THEN 'URGENT: Immediate retention campaign needed'
        WHEN churn_rate > 40 THEN 'Implement proactive outreach program'
        WHEN churn_rate < 10 THEN 'Success pattern - replicate for other segments'
        ELSE 'Standard monitoring'
    END AS recommended_action
FROM segment_risk
ORDER BY risk_score DESC, churn_rate DESC, total_segment_revenue DESC;

-- =================================================================
-- INTERPRETATION GUIDE
-- =================================================================
-- Critical Priority Segments: Focus 80% of retention budget here
-- High Priority: Implement automated early warning systems
-- Risk Score: Higher = more revenue at stake + higher churn probability
-- Recoverable Revenue: Expected gain from 50% churn reduction
-- 
-- Key Patterns to Look For:
-- 1. High charges + low tenure = price shock churners
-- 2. Low services + month-to-month = low engagement
-- 3. Long tenure + low churn = ideal customer profile to replicate
-- =================================================================
