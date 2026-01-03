"""
Model evaluation utilities for classification tasks.
This module provides functions to evaluate machine learning models
with comprehensive metrics and visualizations.
"""
import os
from typing import Any, Dict, Union, TypedDict, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import joblib
import logging

logger = logging.getLogger(__name__)

# Get the project root directory
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class ModelMetrics(TypedDict):
    """Type definition for model evaluation metrics."""
    Model: str
    Accuracy: float
    Precision: float
    Recall: float
    F1_Score: float
    ROC_AUC: float

def evaluate_model(
    model: BaseEstimator,
    X_test: Union[np.ndarray, pd.DataFrame],
    y_test: Union[np.ndarray, pd.Series],
    model_name: str,
    save_plots: bool = True
) -> ModelMetrics:
    """
    Evaluate a classification model and generate performance metrics and visualizations.
    
    Args:
        model: Trained scikit-learn classifier with predict and predict_proba methods
        X_test: Test features (numpy array or pandas DataFrame)
        y_test: True labels for the test set (numpy array or pandas Series)
        model_name: Name of the model for display and file naming
        save_plots: Whether to save the generated plots to disk
        
    Returns:
        Dictionary containing evaluation metrics
        
    Raises:
        ValueError: If input validation fails
        RuntimeError: If model prediction fails
    """
    # Input validation
    if not hasattr(model, 'predict'):
        raise ValueError("Model must have a predict method")
    if not hasattr(model, 'predict_proba'):
        raise ValueError("Model must have predict_proba method for ROC-AUC")
    if len(X_test) != len(y_test):
        raise ValueError("X_test and y_test must have the same length")
    if len(X_test) == 0:
        raise ValueError("Input data cannot be empty")
    
    try:
        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)  # ← ADD zero_division
        recall = recall_score(y_test, y_pred, zero_division=0)        # ← ADD zero_division
        f1 = f1_score(y_test, y_pred, zero_division=0)                # ← ADD zero_division
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        # Print metrics
        print(f"\n{'='*70}")
        print(f"{model_name} Performance")
        print('='*70)
        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        print(f"ROC-AUC:   {roc_auc:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Not Churned', 'Churned']))
        
        # Plot confusion matrix
        _plot_confusion_matrix(
            y_true=y_test,
            y_pred=y_pred,
            model_name=model_name,
            save_plot=save_plots
        )
        
        return {
            'Model': model_name,
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1_Score': f1,
            'ROC_AUC': roc_auc
        }
    
    except Exception as e:
        logger.error(f"Error during model evaluation: {str(e)}")
        raise RuntimeError(f"Failed to evaluate model: {str(e)}")


def _plot_confusion_matrix(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
    model_name: str,
    save_plot: bool = True
):
    try:
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                    xticklabels=['Not Churned', 'Churned'],
                    yticklabels=['Not Churned', 'Churned'])
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title(f'Confusion Matrix - {model_name}')
        plt.tight_layout()

        if save_plot:
            figures_dir = os.path.join(ROOT_DIR, 'reports', 'figures')
            os.makedirs(figures_dir, exist_ok=True)
            out_path = os.path.join(figures_dir, f"{model_name.replace(' ', '_').lower()}_confusion_matrix.png")
            plt.savefig(out_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrix saved to {out_path}")

        plt.show()
    except Exception as e:
        logger.warning(f"Failed to plot confusion matrix: {str(e)}")

def compare_models(evaluation_results: list) -> pd.DataFrame:
    """
    Compare multiple model evaluation results.
    
    Args:
        evaluation_results: List of ModelMetrics dictionaries
        
    Returns:
        DataFrame with comparison of all models sorted by ROC-AUC
    """
    if not evaluation_results:
        logger.warning("No evaluation results provided")
        return pd.DataFrame()
    
    try:
        df = pd.DataFrame(evaluation_results)
        df = df.round(4)
        
        # Sort by ROC_AUC descending
        if 'ROC_AUC' in df.columns:
            df = df.sort_values('ROC_AUC', ascending=False)
        
        # Highlight best model
        best_model = df.iloc[0]['Model'] if len(df) > 0 else None
        
        print("\n" + "=" * 70)
        print("MODEL COMPARISON SUMMARY")
        print("=" * 70)
        print(f"\n{df.to_string(index=False)}")
        
        if best_model:
            best_roc = df.iloc[0]['ROC_AUC']
            print(f"\n🏆 BEST MODEL: {best_model} (ROC-AUC: {best_roc:.4f})")
        
        return df
    
    except Exception as e:
        logger.error(f"Error comparing models: {str(e)}")
        return pd.DataFrame()
