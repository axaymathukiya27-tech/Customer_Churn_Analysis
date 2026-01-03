-- =================================================================
-- RFM SEGMENTATION ANALYSIS
-- =================================================================
-- Purpose: Segment customers by Recency, Frequency, and Monetary value
-- Business Use: Targeted marketing campaigns based on customer behavior
-- RFM Scale: 1-5 (5 = best, 1 = worst)
-- =================================================================

WITH rfm_base AS (
    SELECT 
        customerID,
        -- RECENCY: How recently active (based on tenure, inverse scoring)
        tenure,
        -- FREQUENCY: Number of services as proxy for engagement
        num_services,
        -- MONETARY: Total revenue contribution
        total_revenue,
        MonthlyCharges,
        Churn,
        Contract
    FROM combined_customer_data
),

-- Calculate RFM scores using NTILE for quintiles
rfm_scores AS (
    SELECT 
        customerID,
        tenure,
        num_services,
        total_revenue,
        MonthlyCharges,
        Contract,
        Churn,
        -- Recency Score (higher tenure = lower recency score, need inverse)
        6 - NTILE(5) OVER (ORDER BY tenure DESC) AS recency_score,
        -- Frequency Score (more services = higher frequency)
        NTILE(5) OVER (ORDER BY num_services ASC) AS frequency_score,
        -- Monetary Score (higher revenue = higher monetary value)
        NTILE(5) OVER (ORDER BY total_revenue ASC) AS monetary_score
    FROM rfm_base
),

-- Create RFM segments based on score combinations
rfm_segments AS (
    SELECT 
        *,
        CONCAT(recency_score, frequency_score, monetary_score) AS rfm_code,
        -- Segment classification
        CASE 
            WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 
                THEN 'Champions'
            WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score >= 4 
                THEN 'Loyal Customers'
            WHEN recency_score >= 4 AND frequency_score <= 2 AND monetary_score >= 3 
                THEN 'Big Spenders'
            WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score <= 3 
                THEN 'Potential Loyalists'
            WHEN recency_score >= 3 AND frequency_score <= 2 AND monetary_score <= 2 
                THEN 'Needs Attention'
            WHEN recency_score <= 2 AND frequency_score >= 4 
                THEN 'At Risk'
            WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score >= 4 
                THEN 'Cant Lose Them'
            WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score <= 2 
                THEN 'Lost'
            ELSE 'Others'
        END AS rfm_segment
    FROM rfm_scores
)

-- Final output with segment summary
SELECT 
    customerID,
    rfm_code,
    rfm_segment,
    recency_score,
    frequency_score,
    monetary_score,
    tenure,
    num_services,
    total_revenue,
    MonthlyCharges,
    Contract,
    Churn
FROM rfm_segments
ORDER BY recency_score DESC, frequency_score DESC, monetary_score DESC;

-- Segment-level summary
SELECT 
    rfm_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(total_revenue), 2) AS avg_revenue,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(tenure), 1) AS avg_tenure,
    ROUND(100.0 * SUM(Churn) / COUNT(*), 2) AS churn_rate,
    -- Segment value
    ROUND(SUM(total_revenue), 2) AS total_segment_value
FROM rfm_segments
GROUP BY rfm_segment
ORDER BY total_segment_value DESC;
