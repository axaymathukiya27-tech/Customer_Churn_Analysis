"""
Utility functions for customer churn analysis project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def save_dataframe(df, filepath, description=""):
    """Save DataFrame to CSV with logging"""
    try:
        df.to_csv(filepath, index=False)
        logger.info(f"{description} saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving {description}: {str(e)}")
        return False

def load_dataframe(filepath):
    """Load DataFrame from CSV with error handling"""
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Loaded data from {filepath} - Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data from {filepath}: {str(e)}")
        return None

def check_missing_values(df):
    """Check and report missing values"""
    missing = df.isnull().sum()
    missing_pct = 100 * missing / len(df)
    missing_table = pd.DataFrame({
        'Column': missing.index,
        'Missing Values': missing.values,
        'Percentage': missing_pct.values
    })
    missing_table = missing_table[missing_table['Missing Values'] > 0].sort_values(
        'Missing Values', ascending=False
    )
    
    if len(missing_table) == 0:
        logger.info("No missing values found")
    
    
    return missing_table

