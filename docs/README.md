# Customer Churn Analysis - SQL & Power BI Project

## Project Overview
End-to-end customer churn analysis combining Python preprocessing, SQL analytics, and Power BI visualization for actionable business insights.

---

## Folder Structure

customer-churn-analysis/
├── data/ # Raw and processed datasets (.csv)
├── sql/ # All SQL scripts (setup, queries, procedures)
├── exports/ # Query results and features (CSV files)
├── notebooks/ # Python analysis notebooks (.ipynb)
├── dashboards/ # Power BI files and screenshots
├── docs/ # Documentation (README, guides)
└── results/ # Validation screenshots and testing


---

## Quick Start Guide

### 1. Setup Database

- Open MySQL Workbench and run:
  - `sql/01_schema_setup.sql`
- Import `customer_churn_master.csv` using Table Data Import Wizard
- Run validation checks:
  - `sql/03_validation_checks.sql`

### 2. Create Analytics Infrastructure

- Run infrastructure scripts:
  - `sql/04_indexes_and_views.sql`
  - `sql/05_feature_engineering.sql`
  - `sql/06_risk_scoring.sql`

### 3. Run Advanced Queries

- Execute all queries in `sql/queries/`
- Export results to `exports/query_results/`

### 4. Build Dashboard

- Import CSV files from `exports/` into Power BI
- Create dashboard pages: Overview, Segmentation, Retention, Revenue
- Save Power BI dashboard to `dashboards/power_bi/`

---

## Key Business Questions Answered

1. **Which customer segments have highest churn risk?**
2. **What are the top drivers of customer churn?**
3. **Who are the high-risk customers needing retention?**
4. **How much revenue is lost to churn by contract type?**
5. **Does service bundling reduce churn?**
6. **Which payment methods correlate with higher churn?**
7. **How does churn vary across customer tenure cohorts?**

---

## Data Sources

- **Original Dataset:** Telco Customer Churn
- **Preprocessing:** Python (Pandas, NumPy)
- **Analysis:** MySQL 8.0
- **Visualization:** Power BI

## Technologies Used

- **Python 3.13** (Data preprocessing)
- **MySQL 8.0** (Advanced analytics)
- **Power BI** (Dashboard visualization)
- **MySQL Workbench** (Database management)

---

## Results

- **Churn Rate:** 27.05%
- **Total Customers:** 7,286
- **Revenue at Risk:** $[your value]
- **High-Risk Customers:** 892

---

## Author
Axay Mathukiya

## Date
October 2025

---
