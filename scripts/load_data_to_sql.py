"""
Script to load customer churn data from CSV to SQL database
Supports MySQL, PostgreSQL, and SQL Server
"""

import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    'type': 'mysql',  # Options: 'mysql', 'postgresql', 'sqlserver'
    'host': 'localhost',
    'port': 3306,  # MySQL: 3306, PostgreSQL: 5432, SQL Server: 1433
    'database': 'customer_churn_db',
    'username': 'your_username',
    'password': 'your_password'
}

def create_connection_string(config):
    """
    Create SQLAlchemy connection string based on database type
    """
    db_type = config['type']
    
    if db_type == 'mysql':
        conn_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    elif db_type == 'postgresql':
        conn_string = f"postgresql+psycopg2://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    elif db_type == 'sqlserver':
        conn_string = f"mssql+pyodbc://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?driver=ODBC+Driver+17+for+SQL+Server"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    return conn_string

def load_csv_to_sql(csv_filepath, table_name, if_exists='replace'):
    """
    Load data from CSV file to SQL database
    """
    try:
        logger.info(f"Starting data load from {csv_filepath} to table '{table_name}'")
        
        if not os.path.exists(csv_filepath):
            logger.error(f"CSV file not found: {csv_filepath}")
            return False
        
        logger.info("Reading CSV file...")
        df = pd.read_csv(csv_filepath)
        logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
        
        print(df.head())
        print(f"\nData types:\n{df.dtypes}")
        
        logger.info("Connecting to database...")
        conn_string = create_connection_string(DB_CONFIG)
        engine = create_engine(conn_string)
        
        with engine.connect() as conn:
            logger.info("Database connection successful")
        
        logger.info(f"Loading data to table '{table_name}'...")
        start_time = datetime.now()
        
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=1000,
            method='multi'
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Data loaded successfully in {duration:.2f} seconds")
        logger.info(f"Total rows inserted: {len(df)}")
        
        # Verify data load
        logger.info("Verifying data load...")
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.fetchone()
            logger.info(f"Verified: {count} rows in table '{table_name}'")
        
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"Error loading data to SQL: {str(e)}", exc_info=True)
        return False

def main():
    print("="*70)
    print("LOAD CSV DATA TO SQL DATABASE")
    print("="*70)
    
    raw_data_path = '../data/raw/customer_churn_raw.csv'
    processed_data_path = '../data/processed/customer_churn_cleaned.csv'
    
    logger.info("\n--- Loading RAW data ---")
    success_raw = load_csv_to_sql(
        csv_filepath=raw_data_path,
        table_name='customers_raw',
        if_exists='replace'
    )
    
    logger.info("\n--- Loading PROCESSED data ---")
    success_processed = load_csv_to_sql(
        csv_filepath=processed_data_path,
        table_name='customers',
        if_exists='replace'
    )
    
    print("\n" + "="*70)
    print("DATA LOAD SUMMARY")
    print("="*70)
    print(f"Raw data load: {'✓ SUCCESS' if success_raw else '✗ FAILED'}")
    print(f"Processed data load: {'✓ SUCCESS' if success_processed else '✗ FAILED'}")
    print("="*70)

if __name__ == "__main__":
    main()
