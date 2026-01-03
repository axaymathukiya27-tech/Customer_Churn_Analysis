-- =================================================================
-- HIGH-RISK CUSTOMER IDENTIFICATION - Proactive Retention Targets
-- =================================================================
-- Purpose: Identify active customers most likely to churn for immediate intervention
-- Business Question: Who should our retention team contact this week?
-- Insights Expected: New customers paying above-average prices without service bundles
--                    are prime churn risks requiring immediate attention
-- =================================================================

-- Multi-factor risk assessment combining tenure, pricing, and engagement
-- This generates a prioritized list for retention campaigns
WITH customer_risk_factors AS (
    SELECT
        customerID,
        tenure,
        tenure_group,
        MonthlyCharges,
        total_revenue,
        num_services,
        Contract,
        PaymentMethod,
        PaperlessBilling,
        -- Calculate company-wide benchmarks
        (SELECT ROUND(AVG(MonthlyCharges), 2) FROM combined_customer_data) AS avg_company_charge,
        (SELECT ROUND(AVG(num_services), 1) FROM combined_customer_data) AS avg_company_services,
        -- Risk factor: New customer (< 6 months)
        CASE WHEN tenure < 6 THEN 1 ELSE 0 END AS is_new_customer,
        -- Risk factor: High monthly charges
        CASE WHEN MonthlyCharges > (SELECT AVG(MonthlyCharges) FROM combined_customer_data) 
             THEN 1 ELSE 0 END AS has_high_charges,
        -- Risk factor: Low service adoption
        CASE WHEN num_services < 3 THEN 1 ELSE 0 END AS has_low_services,
        -- Risk factor: Month-to-month contract
        CASE WHEN Contract = 'Month-to-month' THEN 1 ELSE 0 END AS is_monthly_contract,
        -- Risk factor: Manual payment (higher friction)
        CASE WHEN PaymentMethod IN ('Mailed check', 'Electronic check') THEN 1 ELSE 0 END AS manual_payment
    FROM combined_customer_data
    WHERE Churn = 0  -- Only active customers who can still be retained
),
risk_scored_customers AS (
    SELECT
        *,
        -- Calculate composite risk score (weighted factors)
        (is_new_customer * 3 +        -- 30% weight: new customers highest risk
         has_high_charges * 2.5 +      -- 25% weight: price sensitivity
         has_low_services * 2 +        -- 20% weight: low engagement
         is_monthly_contract * 1.5 +   -- 15% weight: no commitment
         manual_payment * 1            -- 10% weight: payment friction
        ) AS composite_risk_score,
        -- Calculate potential revenue loss if this customer churns
        ROUND(MonthlyCharges * 12, 2) AS annual_revenue_at_risk,
        -- Price premium vs company average
        ROUND(((MonthlyCharges - avg_company_charge) / avg_company_charge) * 100, 1) AS price_premium_pct
    FROM customer_risk_factors
)

SELECT 
    customerID,
    tenure,
    tenure_group,
    MonthlyCharges,
    total_revenue,
    num_services,
    Contract,
    PaymentMethod,
    composite_risk_score,
    annual_revenue_at_risk,
    price_premium_pct,
    -- Prioritize by risk score and revenue impact
    CASE 
        WHEN composite_risk_score >= 7 AND annual_revenue_at_risk > 1000 THEN 'Tier 1: Contact Today'
        WHEN composite_risk_score >= 5 OR annual_revenue_at_risk > 800 THEN 'Tier 2: Contact This Week'
        WHEN composite_risk_score >= 3 THEN 'Tier 3: Monitor Closely'
        ELSE 'Standard Monitoring'
    END AS retention_priority,
    -- Suggest specific retention tactics
    CASE 
        WHEN has_high_charges = 1 AND num_services < 3 THEN 'Offer service bundle discount'
        WHEN is_new_customer = 1 AND MonthlyCharges > 80 THEN 'Provide onboarding support + loyalty discount'
        WHEN is_monthly_contract = 1 AND tenure < 12 THEN 'Incentivize annual contract with 10% discount'
        WHEN manual_payment = 1 THEN 'Promote autopay with $5/month discount'
        ELSE 'Standard retention offer'
    END AS recommended_intervention
FROM risk_scored_customers
WHERE composite_risk_score >= 3  -- Only customers with meaningful risk
ORDER BY 
    composite_risk_score DESC, 
    annual_revenue_at_risk DESC,
    MonthlyCharges DESC
LIMIT 500;  -- Top 500 highest-risk customers for immediate action

-- =================================================================
-- INTERPRETATION GUIDE
-- =================================================================
-- Composite Risk Score:
-- - 7-10: Critical risk - immediate intervention required
-- - 5-6: High risk - proactive outreach needed
-- - 3-4: Moderate risk - monitor and engage
--
-- Retention Strategy Priority:
-- 1. Tier 1: Personal call from account manager + custom retention offer
-- 2. Tier 2: Targeted email campaign with value demonstration
-- 3. Tier 3: Automated engagement emails + usage tips
--
-- Expected Outcome: 15-25% churn reduction in targeted segments
-- =================================================================
