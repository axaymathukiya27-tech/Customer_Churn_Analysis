"""
Master script to run complete customer churn analysis pipeline
Executes: Data Loading → Cleaning → EDA → Model Training → Evaluation
"""
import sys 
import os
import logging
import numpy as np
from datetime import datetime
sys.path.append(os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_preprocessing import ChurnDataPreprocessor
from src.feature_engineering import ChurnFeatureEngineer
from src.model_training import ChurnModelTrainer
from src.visualization import ChurnVisualizer
from src.utils import load_dataframe, save_dataframe

# Get base directory path (project root)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Ensure required directories exist
os.makedirs(os.path.join(base_dir, 'reports'), exist_ok=True)
os.makedirs(os.path.join(base_dir, 'reports', 'metrics'), exist_ok=True)
os.makedirs(os.path.join(base_dir, 'visualizations', 'charts'), exist_ok=True)
os.makedirs(os.path.join(base_dir, 'models'), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(base_dir, 'reports', f'analysis_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main execution function for the entire analysis pipeline
    """
    
    # Get base directory path (project root)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    print("="*70)
    print("CUSTOMER CHURN ANALYSIS - AUTOMATED PIPELINE")
    print("="*70)
    
    try:
        # Step 1: Load Data
        logger.info("Step 1: Loading raw data...")
        df = load_dataframe(os.path.join(base_dir, 'data', 'raw', 'customer_churn_raw.csv'))
        if df is None:
            logger.error("Failed to load data. Exiting.")
            return
        
        logger.info(f"Loaded {len(df)} records")
        
        # Step 2: Preprocess Data
        logger.info("Step 2: Preprocessing data...")
        preprocessor = ChurnDataPreprocessor()
        df_clean = preprocessor.clean_data(df.copy())
        
        # Save cleaned data
        save_dataframe(df_clean, os.path.join(base_dir, 'data', 'processed', 'customer_churn_cleaned.csv'),
                      'Cleaned dataset')
        
        # Step 3: Feature Engineering
        logger.info("Step 3: Engineering features...")
        engineer = ChurnFeatureEngineer()
        df_engineered = engineer.engineer_features(df_clean.copy())
        
        # Step 4: Prepare for modeling
        logger.info("Step 4: Preparing data for modeling...")
        if 'Churn' not in df_engineered.columns:
            logger.error("Target variable 'Churn' not found")
            return
            
        # Print Churn distribution before preprocessing
        logger.info(f"Churn distribution before preprocessing: \n{df_engineered['Churn'].value_counts()}")
        
        X_scaled, y = preprocessor.preprocess_pipeline(df_engineered, target_col='Churn', fit=True)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
        
        # Step 5: Train Models
        logger.info("Step 5: Training machine learning models...")
        trainer = ChurnModelTrainer()
        models = trainer.train_all_models(X_train, y_train, balance_data=True)
        
        logger.info(f"Trained {len(models)} models successfully")
        
        # Step 6: Cross-validation
        logger.info("Step 6: Running cross-validation...")
        cv_results = trainer.cross_validate(X_train, y_train, cv=5)
        
        # Step 7: Evaluate on test set
        logger.info("Step 7: Evaluating models on test set...")
        from sklearn.metrics import accuracy_score, roc_auc_score
        
        # Handle missing values in test set
        if isinstance(X_test, np.ndarray):
            X_test = np.nan_to_num(X_test, nan=0)
        else:
            X_test = X_test.fillna(X_test.mean())
        
        results = []
        for model_name, model in models.items():
            try:
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]
                
                accuracy = accuracy_score(y_test, y_pred)
                roc_auc = roc_auc_score(y_test, y_pred_proba)
                
                results.append({
                    'Model': model_name,
                    'Accuracy': accuracy,
                    'ROC-AUC': roc_auc
                })
                
                logger.info(f"{model_name}: Accuracy={accuracy:.4f}, ROC-AUC={roc_auc:.4f}")
            except Exception as e:
                logger.error(f"Error evaluating {model_name}: {str(e)}")
                continue
        
        # Save best model
        best_model_name = max(results, key=lambda x: x['ROC-AUC'])['Model']
        logger.info(f"Best model: {best_model_name}")
        
        trainer.save_model(best_model_name, os.path.join(base_dir, 'models', 'best_model.pkl'))
        
        # Step 8: Generate visualizations
        logger.info("Step 8: Generating visualizations...")
        visualizer = ChurnVisualizer()
        
        # Churn distribution
        visualizer.plot_churn_distribution(
            y, 
            save_path=os.path.join(base_dir, 'visualizations', 'charts', 'churn_distribution.png')
        )
        
        # ROC curve for best model
        best_model = models[best_model_name]
        y_pred_proba = best_model.predict_proba(X_test)[:, 1]
        visualizer.plot_roc_curve(
            y_test, 
            y_pred_proba, 
            model_name=best_model_name,
            save_path=os.path.join(base_dir, 'visualizations', 'charts', f'roc_curve_{best_model_name.lower().replace(" ", "_")}.png')
        )
        
        logger.info("Visualizations saved successfully")
        
        # Step 9: Save results summary
        import pandas as pd
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(base_dir, 'reports', 'metrics', 'model_comparison.csv'), index=False)
        
        logger.info("Results summary saved")
        
        # Final summary
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE!")
        print("="*70)
        print(f"\nBest Model: {best_model_name}")
        print(f"ROC-AUC Score: {max(results, key=lambda x: x['ROC-AUC'])['ROC-AUC']:.4f}")
        print(f"\nResults saved to: reports/metrics/model_comparison.csv")
        print(f"Model saved to: models/best_model.pkl")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
