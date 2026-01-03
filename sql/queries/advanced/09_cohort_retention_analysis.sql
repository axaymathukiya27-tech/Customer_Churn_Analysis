-- =================================================================
-- COHORT RETENTION ANALYSIS WITH LAG/LEAD
-- =================================================================
-- Purpose: Analyze customer retention patterns over tenure cohorts
-- Techniques Used: LAG, LEAD, window functions, cohort analysis
-- =================================================================

WITH tenure_cohorts AS (
    SELECT
        tenure_group,
        COUNT(*) AS cohort_size,
        SUM(Churn) AS churned,
        ROUND(100.0 * SUM(Churn) / COUNT(*), 2) AS churn_rate,
        ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
        ROUND(SUM(total_revenue), 2) AS cohort_revenue,
        
        -- Compare to previous cohort
        LAG(COUNT(*)) OVER (ORDER BY 
            CASE tenure_group
                WHEN '0-1 year' THEN 1
                WHEN '1-2 years' THEN 2
                WHEN '2-4 years' THEN 3
                WHEN '4+ years' THEN 4
            END
        ) AS prev_cohort_size,
        
        LAG(ROUND(100.0 * SUM(Churn) / COUNT(*), 2)) OVER (ORDER BY 
            CASE tenure_group
                WHEN '0-1 year' THEN 1
                WHEN '1-2 years' THEN 2
                WHEN '2-4 years' THEN 3
                WHEN '4+ years' THEN 4
            END
        ) AS prev_churn_rate,
        
        -- Look ahead to next cohort
        LEAD(COUNT(*)) OVER (ORDER BY 
            CASE tenure_group
                WHEN '0-1 year' THEN 1
                WHEN '1-2 years' THEN 2
                WHEN '2-4 years' THEN 3
                WHEN '4+ years' THEN 4
            END
        ) AS next_cohort_size
        
    FROM combined_customer_data
    GROUP BY tenure_group
)

SELECT
    tenure_group,
    cohort_size,
    churned,
    churn_rate,
    avg_monthly_charges,
    cohort_revenue,
    
    -- Calculate retention rate
    ROUND(100.0 - churn_rate, 2) AS retention_rate,
    
    -- Cohort-to-cohort retention (what % moved to next cohort)
    ROUND(100.0 * next_cohort_size / cohort_size, 2) AS progression_rate,
    
    -- Change from previous cohort
    ROUND(churn_rate - prev_churn_rate, 2) AS churn_rate_change,
    
    -- Retention improvement vs previous cohort
    CASE
        WHEN prev_churn_rate IS NOT NULL THEN
            ROUND(100 * (prev_churn_rate - churn_rate) / prev_churn_rate, 2)
        ELSE NULL
    END AS retention_improvement_pct
    
FROM tenure_cohorts
ORDER BY 
    CASE tenure_group
        WHEN '0-1 year' THEN 1
        WHEN '1-2 years' THEN 2
        WHEN '2-4 years' THEN 3
        WHEN '4+ years' THEN 4
    END;
