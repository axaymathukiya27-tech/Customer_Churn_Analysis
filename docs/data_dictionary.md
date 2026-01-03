# Data Dictionary
## Customer Churn Analysis Database

**Last Updated:** October 29, 2025  
**Database:** customer_churn_db  
**Primary Table:** combined_customer_data

---

## Table: combined_customer_data

### Demographic Fields

| Field | Type | Description | Example Values | Business Purpose |
|-------|------|-------------|----------------|------------------|
| customerID | VARCHAR(50) | Unique customer identifier (Primary Key) | 7590-VHVEG | Links to CRM systems |
| gender | VARCHAR(10) | Customer gender | Male, Female | Demographic segmentation |
| SeniorCitizen | TINYINT | Senior citizen flag (1=Yes, 0=No) | 0, 1 | Age-based targeting |
| Partner | TINYINT | Has partner flag (1=Yes, 0=No) | 0, 1 | Household analysis |
| Dependents | TINYINT | Has dependents flag (1=Yes, 0=No) | 0, 1 | Family size segmentation |
| family_size | TINYINT | Calculated family size (Partner + Dependents) | 0, 1, 2 | Household complexity metric |

### Service Subscription Fields

| Field | Type | Description | Example Values | Business Purpose |
|-------|------|-------------|----------------|------------------|
| tenure | INT | Months as customer | 1, 12, 72 | Customer loyalty metric |
| tenure_group | VARCHAR(30) | Tenure categorized into buckets | '0-1 year', '1-2 years', '2-4 years', '4+ years' | Cohort analysis |
| PhoneService | VARCHAR(10) | Phone service subscription | Yes, No | Service penetration |
| MultipleLines | VARCHAR(20) | Multiple phone lines | Yes, No, No phone service | Upsell opportunity |
| InternetService | VARCHAR(20) | Internet service type | DSL, Fiber optic, No | Core service indicator |
| OnlineSecurity | VARCHAR(20) | Online security add-on | Yes, No, No internet service | Add-on penetration |
| OnlineBackup | VARCHAR(20) | Online backup add-on | Yes, No, No internet service | Add-on penetration |
| DeviceProtection | VARCHAR(20) | Device protection add-on | Yes, No, No internet service | Add-on penetration |
| TechSupport | VARCHAR(20) | Tech support add-on | Yes, No, No internet service | Support services |
| StreamingTV | VARCHAR(20) | Streaming TV service | Yes, No, No internet service | Entertainment service |
| StreamingMovies | VARCHAR(20) | Streaming movies service | Yes, No, No internet service | Entertainment service |
| num_services | TINYINT | Total count of active services (0-8) | 0, 3, 7 | Service bundling metric |

### Contract & Billing Fields

| Field | Type | Description | Example Values | Business Purpose |
|-------|------|-------------|----------------|------------------|
| Contract | VARCHAR(30) | Contract type | Month-to-month, One year, Two year | Commitment level |
| is_monthly_contract | TINYINT | Month-to-month flag (1=Yes, 0=No) | 0, 1 | High-risk indicator |
| PaperlessBilling | TINYINT | Paperless billing flag (1=Yes, 0=No) | 0, 1 | Digital engagement |
| paperless_billing_binary | TINYINT | Same as PaperlessBilling (duplicate) | 0, 1 | Feature engineering |
| PaymentMethod | VARCHAR(50) | Payment method | Electronic check, Mailed check, Bank transfer, Credit card | Payment friction indicator |

### Financial Fields

| Field | Type | Description | Example Values | Business Purpose |
|-------|------|-------------|----------------|------------------|
| MonthlyCharges | DECIMAL(9,2) | Current monthly charges | 29.85, 89.95 | Revenue per customer |
| TotalCharges | DECIMAL(12,2) | Lifetime charges to date | 1889.50, 5681.00 | Historical value |
| total_revenue | DECIMAL(12,2) | Same as TotalCharges (duplicate) | 1889.50 | Feature engineering |
| charge_category | VARCHAR(20) | Charges categorized into buckets | Low, Medium, High | Pricing tier segmentation |
| charge_ratio | DECIMAL(9,6) | MonthlyCharges / TotalCharges | 0.015850 | Charge acceleration metric |

### Derived & Target Fields

| Field | Type | Description | Example Values | Business Purpose |
|-------|------|-------------|----------------|------------------|
| Churn | TINYINT | **TARGET VARIABLE** - Customer churned (1=Yes, 0=No) | 0, 1 | Prediction target |
| is_new_customer | TINYINT | Tenure <= 6 months (1=Yes, 0=No) | 0, 1 | Early churn risk |
| is_long_term | TINYINT | Tenure > 24 months (1=Yes, 0=No) | 0, 1 | Loyalty indicator |

---

## Field Categories & Usage

### Risk Scoring Inputs
- `tenure_group`, `charge_category`, `num_services`, `is_monthly_contract`

### Segmentation Dimensions
- `tenure_group`, `charge_category`, `Contract`, `PaymentMethod`

### Churn Drivers
- `MonthlyCharges`, `tenure`, `num_services`, `Contract`, `is_monthly_contract`

### Revenue Metrics
- `MonthlyCharges`, `TotalCharges`, `total_revenue`

---

## Data Quality Notes

- **Missing Values:** All critical fields validated (no nulls in customerID, MonthlyCharges, Churn)
- **Data Source:** Python preprocessing → `combined_customer_data.csv` → MySQL
- **Validation Status:** ✓ Passed (see validation.md)
- **Row Count:** 7,286 customers
- **Churn Rate:** 27.05%
