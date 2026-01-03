import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, auc, roc_auc_score
import logging
from typing import List, Tuple, Union
from sklearn.base import BaseEstimator

logger = logging.getLogger(__name__)

class ChurnVisualizer:
    """
    Create comprehensive visualizations for churn analysis using matplotlib only
    """

    def __init__(self):
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10

    def plot_churn_distribution(self, y, save_path=None):
        """
        Plot churn distribution with percentages
        """
        plt.figure(figsize=(8, 6))
        # Convert y to numeric type and get value counts
        y_numeric = pd.to_numeric(y)
        churn_counts = pd.Series(y_numeric).value_counts().sort_index()
        colors = ['steelblue', 'salmon']
        bars = plt.bar(churn_counts.index, churn_counts.values, color=colors, edgecolor='black')
        plt.title('Churn Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Churn (0=No, 1=Yes)', fontsize=12)
        plt.ylabel('Count', fontsize=12)

        total = len(y)
        for i, (v, bar) in enumerate(zip(churn_counts.values, bars)):
            percentage = (v / total) * 100
            plt.text(bar.get_x() + bar.get_width()/2, v + 50, 
                     f'{v}\n({percentage:.1f}%)', ha='center', fontsize=12, fontweight='bold')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_tenure_segments_churn(self, df, tenure_col='tenure', target='Churn', save_path=None):
        plt.figure(figsize=(10, 6))
        df_local = df.copy()
        if tenure_col not in df_local.columns or target not in df_local.columns:
            return
        bins = [0, 12, 24, 48, 72]
        labels = ['0-1 year', '1-2 years', '2-4 years', '4+ years']
        df_local['__tenure_segment'] = pd.cut(df_local[tenure_col].fillna(0), bins=bins, labels=labels, include_lowest=True)
        churn_rates = df_local.groupby('__tenure_segment')[target].mean().reindex(labels)
        bars = plt.bar(churn_rates.index.astype(str), churn_rates.values * 100, color='salmon', edgecolor='black')
        for bar in bars:
            h = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., h + 1, f'{h:.1f}%', ha='center', va='bottom', fontweight='bold')
        plt.title('Churn Rate by Tenure Segments', fontsize=14, fontweight='bold')
        plt.xlabel('Tenure Segment', fontsize=12)
        plt.ylabel('Churn Rate (%)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_roc_curve(self, y_true, y_pred_proba, model_name='Model', save_path=None):
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'AUC = {roc_auc:.3f}')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(f'ROC Curve - {model_name}', fontsize=14, fontweight='bold')
        plt.legend(loc='lower right')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_feature_distributions(self, df, features, target='Churn', save_path=None):
        """
        Plot feature distributions by churn status using matplotlib
        """
        n_features = len(features)
        fig, axes = plt.subplots(nrows=(n_features+1)//2, ncols=2, figsize=(14, 5*((n_features+1)//2)))
        axes = axes.flatten()

        for idx, feature in enumerate(features):
            ax = axes[idx]
            if df[feature].dtype in ['int64', 'float64']:
                churn_groups = [df[df[target] == 0][feature].dropna(), 
                                df[df[target] == 1][feature].dropna()]
                bp = ax.boxplot(churn_groups, labels=['No', 'Yes'], patch_artist=True)
                bp['boxes'][0].set_facecolor('steelblue')
                bp['boxes'][1].set_facecolor('salmon')
                ax.set_ylabel(feature, fontsize=11)
            else:
                categories = df[feature].value_counts().index
                width = 0.35
                churned = [len(df[(df[target] == 1) & (df[feature] == cat)]) for cat in categories]
                not_churned = [len(df[(df[target] == 0) & (df[feature] == cat)]) for cat in categories]
                x = np.arange(len(categories))
                ax.bar(x - width/2, not_churned, width, color='steelblue', label='Not Churned', edgecolor='black')
                ax.bar(x + width/2, churned, width, color='salmon', label='Churned', edgecolor='black')
                ax.set_xticks(x)
                ax.set_xticklabels(categories, rotation=45, ha='right')
                ax.legend()

            ax.set_title(f'{feature} vs Churn', fontsize=12, fontweight='bold')
            ax.grid(alpha=0.3)

        for idx in range(n_features, len(axes)):
            fig.delaxes(axes[idx])

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_correlation_heatmap(self, df, save_path=None):
        """
        Plot correlation heatmap for numerical features
        """
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        correlation_matrix = df[numerical_cols].corr()

        plt.figure(figsize=(12, 10))
        im = plt.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        plt.title('Feature Correlation Heatmap', fontsize=16, fontweight='bold')
        plt.xticks(range(len(numerical_cols)), numerical_cols, rotation=45, ha='right')
        plt.yticks(range(len(numerical_cols)), numerical_cols)
        plt.colorbar(im, shrink=0.8)

        for i in range(len(numerical_cols)):
            for j in range(len(numerical_cols)):
                color = 'white' if abs(correlation_matrix.iloc[i, j]) > 0.5 else 'black'
                plt.text(j, i, f"{correlation_matrix.iloc[i, j]:.2f}",
                         ha='center', va='center', color=color, fontsize=9)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()



    def plot_multiple_roc_curves(self, y_true, models_dict, save_path=None):
        """
        Plot multiple ROC curves for model comparison
        
        Parameters:
        -----------
        y_true : array-like
            True labels
        models_dict : dict
            Dictionary with model names as keys and predicted probabilities as values
        """
        plt.figure(figsize=(10, 8))
        colors = ['darkorange', 'green', 'red', 'purple', 'brown']
        
        for i, (model_name, y_pred_proba) in enumerate(models_dict.items()):
            fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, lw=2, color=colors[i % len(colors)],
                     label=f'{model_name} (AUC = {roc_auc:.3f})')
        
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
                 label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curves - Model Comparison', fontsize=14, fontweight='bold')
        plt.legend(loc='lower right', fontsize=10)
        plt.grid(alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


    def plot_churn_rate_by_category(self, df, category_col, target='Churn', save_path=None):

        plt.figure(figsize=(10, 6))
        
        # Calculate churn rates
        churn_rates = df.groupby(category_col)[target].mean().sort_values(ascending=False)
        
        # Create bar plot
        bars = plt.bar(churn_rates.index.astype(str), churn_rates.values * 100,
                      color='salmon', edgecolor='black')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.title(f'Churn Rate by {category_col}', fontsize=14, fontweight='bold')
        plt.xlabel(category_col, fontsize=12)
        plt.ylabel('Churn Rate (%)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Add horizontal line for overall churn rate
        overall_churn = df[target].mean() * 100
        plt.axhline(y=overall_churn, color='red', linestyle='--', 
                   label=f'Overall Churn Rate: {overall_churn:.1f}%')
        
        plt.legend()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_revenue_impact(self, df, monthly_charges_col='MonthlyCharges', 
                           target='Churn', save_path=None):
        """
        Plot revenue impact analysis
        """
        churned_revenue = df[df[target] == 1][monthly_charges_col].sum()
        retained_revenue = df[df[target] == 0][monthly_charges_col].sum()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Revenue distribution
        data = [retained_revenue, churned_revenue]
        colors = ['steelblue', 'salmon']
        labels = ['Retained Customers', 'Churned Customers']
        wedges, texts, autotexts = ax1.pie(data, labels=labels, colors=colors, autopct='%1.1f%%',
                                            startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax1.set_title('Revenue Distribution by Churn Status', fontsize=14, fontweight='bold')
        
        # Average charges comparison
        avg_charges_retained = df[df[target] == 0][monthly_charges_col].mean()
        avg_charges_churned = df[df[target] == 1][monthly_charges_col].mean()
        
        ax2.bar(['Retained', 'Churned'], [avg_charges_retained, avg_charges_churned], 
                color=['steelblue', 'salmon'], edgecolor='black')
        ax2.set_title('Average Monthly Charges', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Charges ($)', fontsize=11)
        ax2.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate([avg_charges_retained, avg_charges_churned]):
            ax2.text(i, v + 1, f'${v:.2f}', ha='center', fontweight='bold')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
