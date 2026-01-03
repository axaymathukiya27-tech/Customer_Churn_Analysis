"""
Script to export data from SQL database to CSV files
"""

import pandas as pd
from sqlalchemy import create_engine
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'type': 'mysql',
    'host': 'localhost',
    'port': 3306,
    'database': 'customer_churn_db',
    'username': 'your_username',
    'password': 'your_password'
}

def create_connection_string(config):
    db_type = config['type']
    if db_type == 'mysql':
        return f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    elif db_type == 'postgresql':
        return f"postgresql+psycopg2://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    elif db_type == 'sqlserver':
        return f"mssql+pyodbc://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?driver=ODBC+Driver+17+for+SQL+Server"

def export_query_to_csv(query, output_filepath, description=""):
    try:
        logger.info(f"Starting export: {description}")
        conn_string = create_connection_string(DB_CONFIG)
        engine = create_engine(conn_string)
        
        logger.info("Executing query...")
        df = pd.read_sql(query, engine)
        logger.info(f"Query returned {len(df)} rows and {len(df.columns)} columns")
        
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        
        logger.info(f"Exporting to {output_filepath}...")
        df.to_csv(output_filepath, index=False)
        logger.info(f"✓ Export successful: {output_filepath}")
        
        print(f"\nPreview:")
        print(df.head())
        
        engine.dispose()
        return True
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return False

def export_table_to_csv(table_name, output_filepath):
    query = f"SELECT * FROM {table_name}"
    return export_query_to_csv(query, output_filepath, f"Exporting table '{table_name}'")

def main():
    print("="*70)
    print("EXPORT SQL DATA TO CSV FILES")
    print("="*70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export 1: Full customer table
    logger.info("\n--- Export 1: Full Customer Table ---")
    export1_success = export_table_to_csv(
        table_name='customers',
        output_filepath=f'../data/sql_exports/customers_full_{timestamp}.csv'
    )
    
    # Export 2: Churned customers
    logger.info("\n--- Export 2: Churned Customers ---")
    churn_query = "SELECT * FROM customers WHERE churn = 1 OR churn = 'Yes'"
    export2_success = export_query_to_csv(
        query=churn_query,
        output_filepath=f'../data/sql_exports/churned_customers_{timestamp}.csv',
        description="Churned customers"
    )
    
    # Export 3: Summary statistics
    logger.info("\n--- Export 3: Churn Summary ---")
    summary_query = """
    SELECT 
        COUNT(*) AS total_customers,
        SUM(CASE WHEN churn = 1 THEN 1 ELSE 0 END) AS churned,
        ROUND(100.0 * SUM(CASE WHEN churn = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
    FROM customers
    """
    export3_success = export_query_to_csv(
        query=summary_query,
        output_filepath=f'../data/sql_exports/churn_summary_{timestamp}.csv',
        description="Summary statistics"
    )
    
    # Export 4: Segment Risk Analysis (from queries/01_segment_risk_analysis.sql)
    logger.info("\n--- Export 4: Segment Risk Analysis ---")
    segment_risk_query = """
    SELECT
        tenure_group,
        charge_category,
        COUNT(*) AS total_customers,
        SUM(CASE WHEN Churn = 1 THEN 1 ELSE 0 END) AS churned_customers,
        ROUND(100.0 * SUM(CASE WHEN Churn = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate
    FROM customers
    GROUP BY tenure_group, charge_category
    ORDER BY churn_rate DESC;
    """ # This is an example, use your actual query from 01_segment_risk_analysis.sql
    export4_success = export_query_to_csv(
        query=segment_risk_query,
        output_filepath=f'../data/sql_exports/segment_risk_analysis_{timestamp}.csv',
        description="Segment Risk Analysis"
    )

    # Export 5: Churn Drivers Summary (from queries/02_churn_drivers.sql)
    logger.info("\n--- Export 5: Churn Drivers Summary ---")
    churn_drivers_query = """
    SELECT
        AVG(CASE WHEN Churn = 1 THEN tenure ELSE NULL END) AS avg_tenure_churned,
        AVG(CASE WHEN Churn = 0 THEN tenure ELSE NULL END) AS avg_tenure_retained,
        AVG(CASE WHEN Churn = 1 THEN MonthlyCharges ELSE NULL END) AS avg_monthly_charges_churned,
        AVG(CASE WHEN Churn = 0 THEN MonthlyCharges ELSE NULL END) AS avg_monthly_charges_retained,
        AVG(CASE WHEN Churn = 1 THEN TotalCharges ELSE NULL END) AS avg_total_revenue_churned,
        AVG(CASE WHEN Churn = 0 THEN TotalCharges ELSE NULL END) AS avg_total_revenue_retained
    FROM customers;
    """ # This is an example, use your actual query from 02_churn_drivers.sql
    export5_success = export_query_to_csv(
        query=churn_drivers_query,
        output_filepath=f'../data/sql_exports/churn_drivers_summary_{timestamp}.csv',
        description="Churn Drivers Summary"
    )

    # Export 6: Revenue Loss by Contract Type (from queries/04_revenue_loss_analysis.sql)
    logger.info("\n--- Export 6: Revenue Loss by Contract Type ---")
    revenue_loss_query = """
    SELECT
        Contract,
        COUNT(CASE WHEN Churn = 1 THEN customerID END) AS churned_customers,
        SUM(CASE WHEN Churn = 1 THEN TotalCharges END) AS lost_revenue,
        ROUND(100.0 * COUNT(CASE WHEN Churn = 1 THEN customerID END) / COUNT(customerID), 2) AS churn_rate
    FROM customers
    GROUP BY Contract;
    """ # This is an example, use your actual query from 04_revenue_loss_analysis.sql
    export6_success = export_query_to_csv(
        query=revenue_loss_query,
        output_filepath=f'../data/sql_exports/revenue_loss_by_contract_{timestamp}.csv',
        description="Revenue Loss by Contract Type"
    )
    
    # ... Add more exports for other analytical queries as needed ...

    print("\n" + "="*70)
    print("EXPORT SUMMARY")
    print("="*70)
    print(f"1. Full table: {'✓' if export1_success else '✗'}")
    print(f"2. Churned: {'✓' if export2_success else '✗'}")
    print(f"3. Summary: {'✓' if export3_success else '✗'}")
    print(f"4. Segment Risk: {'✓' if export4_success else '✗'}")
    print(f"5. Churn Drivers: {'✓' if export5_success else '✗'}")
    print(f"6. Revenue Loss: {'✓' if export6_success else '✗'}")
    print("="*70)

if __name__ == "__main__":
    main()
