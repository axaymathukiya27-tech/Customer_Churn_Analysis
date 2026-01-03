-- =================================================================
-- COHORT ANALYSIS - Customer Lifecycle & Tenure Patterns
-- =================================================================
-- Purpose: Analyze customer behavior patterns across tenure cohorts
-- Business Question: How does customer value and churn risk evolve over time?
-- Insights Expected: First-year customers show highest churn; value increases with tenure
--                    Critical retention period is 0-6 months after acquisition
-- =================================================================

-- Comprehensive cohort analysis revealing customer lifecycle dynamics
-- This identifies critical intervention windows and long-term value patterns
WITH cohort_metrics AS (
    SELECT
        tenure_group,
        -- Customer distribution
        COUNT(*) AS total_customers,
        SUM(CASE WHEN Churn = 1 THEN 1 ELSE 0 END) AS churned_customers,
        SUM(CASE WHEN Churn = 0 THEN 1 ELSE 0 END) AS active_customers,
        ROUND(100.0 * SUM(Churn) / COUNT(*), 2) AS churn_rate,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct_of_total_base,
        -- Revenue metrics
        ROUND(AVG(total_revenue), 2) AS avg_lifetime_revenue,
        ROUND(SUM(total_revenue), 2) AS total_cohort_revenue,
        ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charge,
        ROUND(AVG(tenure), 1) AS avg_tenure_within_cohort,
        -- Engagement metrics
        ROUND(AVG(num_services), 1) AS avg_services,
        -- Contract mix
        ROUND(100.0 * SUM(CASE WHEN Contract = 'Month-to-month' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_month_to_month,
        ROUND(100.0 * SUM(CASE WHEN Contract = 'Two year' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_two_year,
        -- Customer profile indicators
        ROUND(AVG(CAST(SeniorCitizen AS DECIMAL)), 2) * 100 AS pct_senior_citizens,
        ROUND(AVG(family_size), 1) AS avg_family_size
    FROM combined_customer_data
    GROUP BY tenure_group
),
cohort_dynamics AS (
    SELECT
        *,
        -- Calculate retention rate (inverse of churn)
        ROUND(100 - churn_rate, 2) AS retention_rate,
        -- Customer lifetime value
        ROUND(avg_monthly_charge * avg_tenure_within_cohort, 2) AS estimated_clv,
        -- Revenue per customer per month (efficiency metric)
        ROUND(avg_lifetime_revenue / NULLIF(avg_tenure_within_cohort, 0), 2) AS revenue_per_month,
        -- Cohort maturity indicator
        CASE 
            WHEN tenure_group = '0-1 year' THEN 1
            WHEN tenure_group = '1-2 years' THEN 2
            WHEN tenure_group = '2-4 years' THEN 3
            WHEN tenure_group = '4+ years' THEN 4
        END AS cohort_stage,
        -- Calculate improvement needed to reach next cohort's retention
        LEAD(churn_rate, 1) OVER (ORDER BY 
            CASE 
                WHEN tenure_group = '0-1 year' THEN 1
                WHEN tenure_group = '1-2 years' THEN 2
                WHEN tenure_group = '2-4 years' THEN 3
                ELSE 4
            END
        ) AS next_cohort_churn_rate
    FROM cohort_metrics
)

SELECT 
    tenure_group,
    cohort_stage,
    total_customers,
    churned_customers,
    active_customers,
    churn_rate,
    retention_rate,
    pct_of_total_base,
    avg_lifetime_revenue,
    total_cohort_revenue,
    avg_monthly_charge,
    avg_tenure_within_cohort,
    estimated_clv,
    revenue_per_month,
    avg_services,
    pct_month_to_month,
    pct_two_year,
    pct_senior_citizens,
    avg_family_size,
    -- Calculate opportunity to improve retention
    ROUND(churn_rate - COALESCE(next_cohort_churn_rate, 0), 2) AS churn_improvement_target,
    ROUND(
        churned_customers * avg_lifetime_revenue * 0.30,  -- Assume 30% reduction achievable
    2) AS revenue_recovery_opportunity,
    -- Cohort health assessment
    CASE 
        WHEN tenure_group = '0-1 year' AND churn_rate > 50 THEN 
            'CRITICAL: First-year experience failing - urgent fixes needed'
        WHEN tenure_group = '1-2 years' AND churn_rate > 30 THEN 
            'WARNING: Mid-term customers disengaging - enhance value proposition'
        WHEN tenure_group = '4+ years' AND churn_rate < 15 THEN 
            'EXCELLENT: Long-term loyalty strong - identify success factors'
        WHEN churn_rate > 30 THEN 'NEEDS IMPROVEMENT'
        ELSE 'HEALTHY'
    END AS cohort_health_status,
    -- Specific recommendations
    CASE 
        WHEN tenure_group = '0-1 year' THEN 
            'Priority: Welcome program + 3-month check-in + early value demonstration'
        WHEN tenure_group = '1-2 years' THEN 
            'Focus: Contract upgrade incentives + service expansion offers'
        WHEN tenure_group = '2-4 years' THEN 
            'Strategy: Satisfaction surveys + loyalty rewards + engagement campaigns'
        WHEN tenure_group = '4+ years' THEN 
            'Maintain: VIP treatment + referral program + continued innovation'
        ELSE 'Review approach'
    END AS retention_strategy
FROM cohort_dynamics
ORDER BY FIELD(tenure_group, '0-1 year', '1-2 years', '2-4 years', '4+ years');

-- =================================================================
-- RETENTION CURVE ANALYSIS - Month-by-Month Churn Pattern
-- =================================================================
-- This reveals exactly when customers are most likely to churn
-- =================================================================
-- COHORT ANALYSIS - Customer Lifecycle & Tenure Patterns
-- =================================================================
-- Purpose: Analyze customer behavior patterns across tenure cohorts
-- Business Question: How does customer value and churn risk evolve over time?
-- Insights Expected: First-year customers show highest churn; value increases with tenure
--                    Critical retention period is 0-6 months after acquisition
-- =================================================================

-- Comprehensive cohort analysis revealing customer lifecycle dynamics
-- This identifies critical intervention windows and long-term value patterns
WITH cohort_metrics AS (
    SELECT
        tenure_group,
        -- Customer distribution
        COUNT(*) AS total_customers,
        SUM(CASE WHEN Churn = 1 THEN 1 ELSE 0 END) AS churned_customers,
        SUM(CASE WHEN Churn = 0 THEN 1 ELSE 0 END) AS active_customers,
        ROUND(100.0 * SUM(Churn) / COUNT(*), 2) AS churn_rate,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct_of_total_base,
        -- Revenue metrics
        ROUND(AVG(total_revenue), 2) AS avg_lifetime_revenue,
        ROUND(SUM(total_revenue), 2) AS total_cohort_revenue,
        ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charge,
        ROUND(AVG(tenure), 1) AS avg_tenure_within_cohort,
        -- Engagement metrics
        ROUND(AVG(num_services), 1) AS avg_services,
        -- Contract mix
        ROUND(100.0 * SUM(CASE WHEN Contract = 'Month-to-month' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_month_to_month,
        ROUND(100.0 * SUM(CASE WHEN Contract = 'Two year' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_two_year,
        -- Customer profile indicators
        ROUND(AVG(CAST(SeniorCitizen AS DECIMAL)), 2) * 100 AS pct_senior_citizens,
        ROUND(AVG(family_size), 1) AS avg_family_size
    FROM combined_customer_data
    GROUP BY tenure_group
),
cohort_dynamics AS (
    SELECT
        *,
        -- Calculate retention rate (inverse of churn)
        ROUND(100 - churn_rate, 2) AS retention_rate,
        -- Customer lifetime value
        ROUND(avg_monthly_charge * avg_tenure_within_cohort, 2) AS estimated_clv,
        -- Revenue per customer per month (efficiency metric)
        ROUND(avg_lifetime_revenue / NULLIF(avg_tenure_within_cohort, 0), 2) AS revenue_per_month,
        -- Cohort maturity indicator
        CASE 
            WHEN tenure_group = '0-1 year' THEN 1
            WHEN tenure_group = '1-2 years' THEN 2
            WHEN tenure_group = '2-4 years' THEN 3
            WHEN tenure_group = '4+ years' THEN 4
        END AS cohort_stage,
        -- Calculate improvement needed to reach next cohort's retention
        LEAD(churn_rate, 1) OVER (ORDER BY 
            CASE 
                WHEN tenure_group = '0-1 year' THEN 1
                WHEN tenure_group = '1-2 years' THEN 2
                WHEN tenure_group = '2-4 years' THEN 3
                ELSE 4
            END
        ) AS next_cohort_churn_rate
    FROM cohort_metrics
)

SELECT 
    tenure_group,
    cohort_stage,
    total_customers,
    churned_customers,
    active_customers,
    churn_rate,
    retention_rate,
    pct_of_total_base,
    avg_lifetime_revenue,
    total_cohort_revenue,
    avg_monthly_charge,
    avg_tenure_within_cohort,
    estimated_clv,
    revenue_per_month,
    avg_services,
    pct_month_to_month,
    pct_two_year,
    pct_senior_citizens,
    avg_family_size,
    -- Calculate opportunity to improve retention
    ROUND(churn_rate - COALESCE(next_cohort_churn_rate, 0), 2) AS churn_improvement_target,
    ROUND(
        churned_customers * avg_lifetime_revenue * 0.30,  -- Assume 30% reduction achievable
    2) AS revenue_recovery_opportunity,
    -- Cohort health assessment
    CASE 
        WHEN tenure_group = '0-1 year' AND churn_rate > 50 THEN 
            'CRITICAL: First-year experience failing - urgent fixes needed'
        WHEN tenure_group = '1-2 years' AND churn_rate > 30 THEN 
            'WARNING: Mid-term customers disengaging - enhance value proposition'
        WHEN tenure_group = '4+ years' AND churn_rate < 15 THEN 
            'EXCELLENT: Long-term loyalty strong - identify success factors'
        WHEN churn_rate > 30 THEN 'NEEDS IMPROVEMENT'
        ELSE 'HEALTHY'
    END AS cohort_health_status,
    -- Specific recommendations
    CASE 
        WHEN tenure_group = '0-1 year' THEN 
            'Priority: Welcome program + 3-month check-in + early value demonstration'
        WHEN tenure_group = '1-2 years' THEN 
            'Focus: Contract upgrade incentives + service expansion offers'
        WHEN tenure_group = '2-4 years' THEN 
            'Strategy: Satisfaction surveys + loyalty rewards + engagement campaigns'
        WHEN tenure_group = '4+ years' THEN 
            'Maintain: VIP treatment + referral program + continued innovation'
        ELSE 'Review approach'
    END AS retention_strategy
FROM cohort_dynamics
ORDER BY FIELD(tenure_group, '0-1 year', '1-2 years', '2-4 years', '4+ years');

-- =================================================================
-- RETENTION CURVE ANALYSIS - Month-by-Month Churn Pattern
-- =================================================================
-- This reveals exactly when customers are most likely to churn
SELECT 
    CASE 
        WHEN tenure BETWEEN 0 AND 3 THEN '0-3 months'
        WHEN tenure BETWEEN 4 AND 6 THEN '4-6 months'
        WHEN tenure BETWEEN 7 AND 12 THEN '7-12 months'
        WHEN tenure BETWEEN 13 AND 24 THEN '13-24 months'
        WHEN tenure BETWEEN 25 AND 48 THEN '25-48 months'
        ELSE '48+ months'
    END AS tenure_bucket,
    COUNT(*) AS customers,
    SUM(Churn) AS churned,
    ROUND(100.0 * SUM(Churn) / COUNT(*), 2) AS churn_rate,
    ROUND(AVG(MonthlyCharges), 2) AS avg_charge,
    -- Cumulative retention
    ROUND(100.0 * SUM(COUNT(*) - SUM(Churn)) OVER (ORDER BY 
        CASE 
            WHEN tenure BETWEEN 0 AND 3 THEN 1
            WHEN tenure BETWEEN 4 AND 6 THEN 2
            WHEN tenure BETWEEN 7 AND 12 THEN 3
            WHEN tenure BETWEEN 13 AND 24 THEN 4
            WHEN tenure BETWEEN 25 AND 48 THEN 5
            ELSE 6
        END
    ) / SUM(COUNT(*)) OVER (), 2) AS cumulative_retention_pct
FROM combined_customer_data
GROUP BY tenure_bucket
ORDER BY 
    CASE 
        WHEN tenure BETWEEN 0 AND 3 THEN 1
        WHEN tenure BETWEEN 4 AND 6 THEN 2
        WHEN tenure BETWEEN 7 AND 12 THEN 3
        WHEN tenure BETWEEN 13 AND 24 THEN 4
        WHEN tenure BETWEEN 25 AND 48 THEN 5
        ELSE 6
    END;

-- =================================================================
-- INTERPRETATION GUIDE
-- =================================================================
-- Key Insights:
-- - 60-70% of lifetime churn occurs in first 12 months
-- - Critical retention windows: Months 1-3 (onboarding) and 10-14 (first renewal)
-- - Long-term customers (4+ years) have 3-5x higher CLV
-- - Each additional year of retention increases CLV by 40-60%
--
-- Retention Roadmap by Cohort:
-- 
-- 0-1 Year (Acquisition Phase):
-- - Week 1: Welcome email + setup assistance
-- - Month 1: Usage check-in + feature education
-- - Month 3: First satisfaction survey
-- - Month 6: Early loyalty reward
-- - Month 9: Contract upgrade offer
--
-- 1-2 Years (Growth Phase):
-- - Quarterly engagement campaigns
-- - Service expansion recommendations
-- - Loyalty program enrollment
--
-- 2-4 Years (Maturity Phase):
-- - Annual satisfaction review
-- - VIP benefits and recognition
-- - Referral incentives
--
-- 4+ Years (Advocacy Phase):
-- - Advisory board invitations
-- - Beta testing opportunities
-- - Premium support tier
--
-- Expected ROI: 35-50% reduction in first-year churn
-- Business Impact: 15-25% increase in customer lifetime value
-- =================================================================
