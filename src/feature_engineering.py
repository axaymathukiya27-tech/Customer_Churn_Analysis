

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os

def create_engineered_features(df):

    print("="*70)
    print("CREATING NEW FEATURES")
    print("="*70)
    
    df_engineered = df.copy()
    
    # ============================================================
    # DATA TYPE VALIDATION AND CONVERSION
    # ============================================================
    print("\n[Data Type Validation]")

    # Ensure numeric columns are actually numeric
    numeric_columns = ['TotalCharges', 'MonthlyCharges', 'tenure']

    for col in numeric_columns:
        if col in df_engineered.columns:
            if df_engineered[col].dtype == 'object':
                original_dtype = df_engineered[col].dtype
                df_engineered[col] = pd.to_numeric(df_engineered[col], errors='coerce')
            
                # Fill any NaN created by conversion
                if df_engineered[col].isnull().any():
                    fill_value = df_engineered[col].median()
                    df_engineered[col].fillna(fill_value, inplace=True)
                    print(f"✓ Converted {col}: {original_dtype} → {df_engineered[col].dtype}, filled {df_engineered[col].isnull().sum()} nulls")
                else:
                    print(f"✓ Converted {col}: {original_dtype} → {df_engineered[col].dtype}")
            else:
                print(f"✓ {col} already numeric ({df_engineered[col].dtype})")
    
    # 1. Tenure-based features
    if 'tenure' in df.columns:
        # Tenure groups
        df_engineered['tenure_group'] = pd.cut(
            df_engineered['tenure'], 
            bins=[0, 12, 24, 48, 72],
            labels=['0-1 year', '1-2 years', '2-4 years', '4+ years']
        )
        print("✓ Created: tenure_group")
        
        # Is new customer (tenure < 12 months)
        df_engineered['is_new_customer'] = (df_engineered['tenure'] < 12).astype(int)
        print("✓ Created: is_new_customer")
        
        # Is long-term customer (tenure > 48 months)
        df_engineered['is_long_term'] = (df_engineered['tenure'] > 48).astype(int)
        print("✓ Created: is_long_term")
    
    # 2. Charges-based features
    if 'MonthlyCharges' in df.columns and 'tenure' in df.columns:
        # Total revenue (MonthlyCharges * tenure)
        df_engineered['total_revenue'] = df_engineered['MonthlyCharges'] * df_engineered['tenure']
        print("✓ Created: total_revenue")
        
        # Average monthly spend category
        df_engineered['charge_category'] = pd.cut(
            df_engineered['MonthlyCharges'],
            bins=[0, 35, 70, 120],
            labels=['Low', 'Medium', 'High']
        )
        print("✓ Created: charge_category")
    
    if 'TotalCharges' in df.columns and 'MonthlyCharges' in df.columns:
        # Price consistency (TotalCharges / (MonthlyCharges * tenure))
        df_engineered['charge_ratio'] = df_engineered['TotalCharges'] / (
            df_engineered['MonthlyCharges'] * df_engineered['tenure'] + 1
        )
        print("✓ Created: charge_ratio")
    
    # 3. Service-based features
    service_cols = ['PhoneService', 'InternetService', 'OnlineSecurity', 
                    'OnlineBackup', 'DeviceProtection', 'TechSupport', 
                    'StreamingTV', 'StreamingMovies']
    
    available_services = [col for col in service_cols if col in df.columns]
    if available_services:
        # Count number of services
        df_engineered['num_services'] = 0
        for col in available_services:
            df_engineered['num_services'] += (df_engineered[col] == 'Yes').astype(int)
        print(f"✓ Created: num_services (counted from {len(available_services)} service columns)")
    
    # 4. Contract and payment features
    if 'Contract' in df.columns:
        # Is month-to-month
        df_engineered['is_monthly_contract'] = (df_engineered['Contract'] == 'Month-to-month').astype(int)
        print("✓ Created: is_monthly_contract")
    
    if 'PaperlessBilling' in df.columns:
        # Paperless billing binary
        df_engineered['paperless_billing_binary'] = (df_engineered['PaperlessBilling'] == 'Yes').astype(int)
        print("✓ Created: paperless_billing_binary")
    
    # 5. Demographics
    if 'SeniorCitizen' in df.columns and 'Partner' in df.columns and 'Dependents' in df.columns:
        # Family score (Partner + Dependents)
        df_engineered['family_size'] = (
            (df_engineered['Partner'] == 'Yes').astype(int) + 
            (df_engineered['Dependents'] == 'Yes').astype(int)
        )
        print("✓ Created: family_size")
    
    print(f"\nNew shape after feature engineering: {df_engineered.shape}")
    print(f"Added {df_engineered.shape[1] - df.shape[1]} new features")
    
    return df_engineered


def encode_categorical_variables(df):

    print("\n" + "="*70)
    print("ENCODING CATEGORICAL VARIABLES")
    print("="*70)
    
    df_encoded = df.copy()
    
    # Get categorical columns (excluding target)
    categorical_cols_to_encode = df_encoded.select_dtypes(include=['object']).columns.tolist()
    categorical_cols_to_encode = [col for col in categorical_cols_to_encode if col != 'Churn']
    
    print(f"\nCategorical columns to encode: {len(categorical_cols_to_encode)}")
    
    for col in categorical_cols_to_encode:
        unique_values = df_encoded[col].nunique()
        
        if unique_values == 2:
            # Binary encoding with LabelEncoder
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            print(f"✓ Label Encoded (binary): {col}")
        else:
            # One-hot encoding for multi-class
            df_encoded = pd.get_dummies(df_encoded, columns=[col], prefix=col, drop_first=True)
            print(f"✓ One-Hot Encoded: {col} ({unique_values} categories)")
    
    print(f"\nShape after encoding: {df_encoded.shape}")
    
    return df_encoded


def handle_missing_values(df):

    print("\n" + "="*70)
    print("HANDLING MISSING VALUES")
    print("="*70)
    
    df_clean = df.copy()
    
    # Check for missing values
    missing = df_clean.isnull().sum()
    missing_cols = missing[missing > 0]
    
    if len(missing_cols) > 0:
        print("\nMissing values found:")
        print(missing_cols)
        
        # Fill with median for numerical, mode for categorical
        for col in missing_cols.index:
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                median_val = df_clean[col].median()
                df_clean[col] = df_clean[col].fillna(median_val)
                print(f"✓ Filled {col} with median ({median_val})")
            else:
                mode_val = df_clean[col].mode()[0]
                df_clean[col] = df_clean[col].fillna(mode_val)
                print(f"✓ Filled {col} with mode ('{mode_val}')")
    else:
        print("\n✓ No missing values found")

    total_missing = df_clean.isnull().sum().sum()
    print(f"\nFinal missing values: {df_clean.isnull().sum().sum()}")
    
    return df_clean


class ChurnFeatureEngineer:
    def engineer_features(self, df):
        return create_engineered_features(df)

def print_feature_engineering_summary(
    df_original: pd.DataFrame,
    df_engineered: pd.DataFrame,
    df_encoded: pd.DataFrame,
    X: pd.DataFrame,
    y: pd.Series,
):
    print("\n" + "="*70)
    print("FEATURE ENGINEERING SUMMARY")
    print("="*70)

    print("\n[Dataset Transformation]:")
    print(f"   Original features: {df_original.shape[1]}")
    print(f"   After engineering: {df_engineered.shape[1]}")
    print(f"   After encoding: {df_encoded.shape[1]}")
    print(f"   Final features for modeling: {X.shape[1]}")

    print("\n[Target Variable]:")
    print(f"   Churn rate (overall): {y.mean():.2%}")
    print(f"   Churned customers: {int(y.sum()):,}")
    print(f"   Retained customers: {int((1 - y).sum()):,}")

    print("\n[✓] Feature Engineering Complete!")
    print("[✓] Data is ready for machine learning modeling")
