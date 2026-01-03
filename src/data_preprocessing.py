"""
Data preprocessing module for customer churn analysis
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import logging

logger = logging.getLogger(__name__)

class ChurnDataPreprocessor:
    """
    Comprehensive data preprocessing for churn analysis
    """
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def clean_data(self, df):
        """
        Clean raw data: handle missing values, duplicates, and data types
        """
        logger.info("Starting data cleaning...")
        
        # Create a copy of the dataframe
        df = df.copy()
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle TotalCharges if exists
        if 'TotalCharges' in df.columns:
            df.loc[:, 'TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
            median_value = df['TotalCharges'].median()
            df.loc[:, 'TotalCharges'] = df['TotalCharges'].fillna(median_value)
        
        # Handle binary columns if present
        binary_cols = ['Churn'] if 'Churn' in df.columns else []
        for col in binary_cols:
            if df[col].dtype == 'object':
                df.loc[:, col] = df[col].map({'Yes': 1, 'No': 0})
        
        # Remove customer ID if present
        if 'customerID' in df.columns:
            df = df.drop('customerID', axis=1)
        
        logger.info(f"Data cleaning completed. Final shape: {df.shape}")
        return df
    
    def encode_categorical(self, df, fit=True):
        """
        Encode categorical variables
        """
        logger.info("Encoding categorical variables...")
        
        # Handle categorical columns (including tenure_group which might be categorical)
        categorical_cols = list(df.select_dtypes(include=['object']).columns)
        if 'tenure_group' in df.columns and df['tenure_group'].dtype != 'object':
            categorical_cols.append('tenure_group')
        
        for col in categorical_cols:
            if col == 'Churn':
                continue
                
            if fit:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            else:
                if col in self.label_encoders:
                    le = self.label_encoders[col]
                    df[col] = df[col].map(lambda x: le.transform([str(x)]) 
                                          if str(x) in le.classes_ else -1)
        
        logger.info(f"Encoded {len(categorical_cols)} categorical columns")
        return df
    
    def scale_features(self, X, fit=True):
        """
        Scale numerical features and handle missing values
        """
        logger.info("Scaling features...")
        
        # Handle missing values
        if isinstance(X, np.ndarray):
            X = np.nan_to_num(X, nan=0)
        else:
            X = X.fillna(X.mean())
        
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def preprocess_pipeline(self, df, target_col='Churn', fit=True):
        """
        Complete preprocessing pipeline
        """
        logger.info("Running full preprocessing pipeline...")
        
        # Create a copy of the dataframe
        df = df.copy()
        
        # Record initial index
        initial_index = df.index
        
        # Separate features and target first
        if target_col in df.columns:
            y = df[target_col].copy()  # Extract target before any processing
            X = df.drop(target_col, axis=1)
        else:
            X = df
            y = None
            
        # Clean features
        X = self.clean_data(X)
        
        # Update y to match X's index after cleaning
        if y is not None:
            y = y[X.index]
            
            # Handle missing values and ensure integer type for target
            if y.isna().any():
                mode_value = y.mode().iloc[0] if not y.mode().empty else 0
                y = y.fillna(mode_value)
            y = y.astype(int)  # Ensure target is integer type
            
        logger.info(f"Target distribution: \n{y.value_counts()}")
        
        # Encode categorical
        X = self.encode_categorical(X, fit=fit)
        
        # Scale features
        X_scaled = self.scale_features(X, fit=fit)
        
        logger.info("Preprocessing pipeline completed")
        
        if y is not None:
            return X_scaled, y
        else:
            return X_scaled
