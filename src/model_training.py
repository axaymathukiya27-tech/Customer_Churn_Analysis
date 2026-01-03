"""
Model training module for customer churn prediction
"""
import numpy as np
import pandas as pd  # ← ADD THIS LINE
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score,train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from datetime import datetime
import json
from pathlib import Path
import os
import joblib
import logging

logger = logging.getLogger(__name__)

class ChurnModelTrainer:
    """
    Train and manage churn prediction models
    """
    
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_model_name = None
    
    def prepare_data(
        self,
        X,
        y,
        test_size=0.2,
        random_state=42,
        scale_data=True,
    ):
        """
        Split data and apply StandardScaler
        """
        logger.info("Splitting data into train and test sets...")

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )

        if scale_data:
            logger.info("Applying StandardScaler...")
            self.scaler = StandardScaler()
            X_train = self.scaler.fit_transform(X_train)
            X_test = self.scaler.transform(X_test)

        return X_train, X_test, y_train, y_test

    
    def handle_imbalance(self, X_train, y_train, method='smote'):
        """
        Handle class imbalance
        """
        # First, handle any missing values
        if isinstance(X_train, np.ndarray):
            X_train = np.nan_to_num(X_train, nan=0)
        else:
            X_train = X_train.fillna(X_train.mean())
        
        if method == 'smote':
            try:
                smote = SMOTE(random_state=42)
                X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
                logger.info(f"Applied SMOTE: {len(y_train)} -> {len(y_resampled)} samples")
                return X_resampled, y_resampled
            except Exception as e:
                logger.error(f"SMOTE failed: {str(e)}")
                logger.warning("Returning original data without balancing")
                return X_train, y_train
        
        return X_train, y_train
    
    def train_random_forest(self, X_train, y_train, **kwargs):
        """
        Train Random Forest model
        """
        logger.info("Training Random Forest...")
        params = {
            'n_estimators': kwargs.get('n_estimators', 100),
            'max_depth': kwargs.get('max_depth', 10),
            'min_samples_split': kwargs.get('min_samples_split', 5),
            'random_state': 42,
            'n_jobs': -1
        }
        
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)
        self.models['Random Forest'] = model
        logger.info("✅ Random Forest trained")
        return model
    
    def train_logistic_regression(self, X_train, y_train):
        """
        Train Logistic Regression model
        """
        logger.info("Training Logistic Regression...")
        model = LogisticRegression(random_state=42, max_iter=1000, solver='lbfgs')
        model.fit(X_train, y_train)
        self.models['Logistic Regression'] = model
        logger.info("✅ Logistic Regression trained")
        return model
    
    def train_gradient_boosting(self, X_train, y_train, **kwargs):
        """
        Train Gradient Boosting model
        """
        logger.info("Training Gradient Boosting...")
        params = {
            'n_estimators': kwargs.get('n_estimators', 100),
            'learning_rate': kwargs.get('learning_rate', 0.1),
            'max_depth': kwargs.get('max_depth', 5),
            'random_state': 42
        }
        
        model = GradientBoostingClassifier(**params)
        model.fit(X_train, y_train)
        self.models['Gradient Boosting'] = model
        logger.info("✅ Gradient Boosting trained")
        return model
    
    def train_all_models(self, X, y, balance_data=True):
        """
        Train all models
        
        Args:
            X: Training features (unscaled)
            y: Training labels
            balance_data: Whether to apply SMOTE for class balancing
            
        Returns:
            dict: Dictionary of trained models
        """
        logger.info("Training all models...")
        X_train, X_test, y_train, y_test = self.prepare_data(X, y)
        if balance_data:
            X_train, y_train = self.handle_imbalance(X_train, y_train)
        
        # Train all models
        self.train_random_forest(X_train, y_train)
        self.train_logistic_regression(X_train, y_train)
        self.train_gradient_boosting(X_train, y_train)
        
        logger.info(f"✅ Trained {len(self.models)} models")
        return X_train, X_test, y_train, y_test
    
    def cross_validate(self, X, y, cv=5):
        """
        Perform cross-validation for all models
        """
        logger.info(f"Running {cv}-fold cross-validation...")
        
        # Handle missing values
        if isinstance(X, np.ndarray):
            X = np.nan_to_num(X, nan=0)
        else:
            X = X.fillna(X.mean())
        
        results = {}
        
        for name, model in self.models.items():
            try:
                scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc', n_jobs=-1)
                results[name] = {
                    'mean': scores.mean(),
                    'std': scores.std(),
                    'scores': scores.tolist()
                }
                logger.info(f"{name}: ROC-AUC = {scores.mean():.4f} (+/- {scores.std():.4f})")
            
            except Exception as e:
                logger.warning(f"Cross-validation failed for {name}: {str(e)}")
                continue
        
        return results
    
    def save_model(self, model_name: str, filepath: str, compress: int = 3, save_metadata: bool = True) -> bool:
        """
        Save trained model to disk with directory creation and validation.
        
        Args:
            model_name (str): Name of the model to save (must exist in self.models)
            filepath (str): Full path where to save the model
            compress (int): Compression level (0-9, default=3)
            save_metadata (bool): Whether to save metadata with model
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate model exists
        if model_name not in self.models:
            logger.error(f"Model '{model_name}' not found. Available models: {list(self.models.keys())}")
            return False
        
        try:
            # Convert to Path object
            filepath = Path(filepath)
            
            # Validate file extension
            if filepath.suffix.lower() not in ('.pkl', '.joblib'):
                logger.warning(f"File extension should be .pkl or .joblib, got {filepath.suffix}")
                filepath = filepath.with_suffix('.pkl')
                logger.info(f"Using {filepath} as the output file")
            
            # Create parent directory if it doesn't exist
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare model data
            model_data = {
                'model': self.models[model_name],
                'metadata': {
                    'model_name': model_name,
                    'saved_at': datetime.now().isoformat(),
                    'model_type': type(self.models[model_name]).__name__,
                    'version': '1.0.0'
                } if save_metadata else None
            }
            
            # Save with compression
            joblib.dump(
                model_data,
                filepath,
                compress=('gzip', compress) if compress > 0 else 0
            )
            
            logger.info(f"✅ Model '{model_name}' successfully saved to {filepath}")
            if save_metadata:
                logger.debug(f"Model metadata: {json.dumps(model_data['metadata'], indent=2)}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to save model '{model_name}': {str(e)}", exc_info=True)
            return False
    
    def load_model(self, filepath: str) -> dict:
        """
        Load trained model with metadata
        
        Args:
            filepath: Path to the saved model file
            
        Returns:
            dict: Dictionary containing 'model' and 'metadata' if available
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.error(f"File not found: {filepath}")
                return None
            
            model_data = joblib.load(filepath)
            logger.info(f"✅ Model loaded from {filepath}")
            
            if isinstance(model_data, dict) and 'model' in model_data:
                if model_data.get('metadata'):
                    logger.info(f"Model metadata: {json.dumps(model_data['metadata'], indent=2)}")
                return model_data
            
            # Handle legacy format (direct model object)
            return {'model': model_data, 'metadata': None}
        
        except Exception as e:
            logger.error(f"❌ Failed to load model from {filepath}: {str(e)}", exc_info=True)
            return None
