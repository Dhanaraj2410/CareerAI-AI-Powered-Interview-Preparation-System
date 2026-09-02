import os
import json
import pathlib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
import joblib

BASE_DIR = pathlib.Path(__file__).resolve().parent

def generate_synthetic_dataset():
    """
    Generate realistic candidate performance dataset.
    Note: The dataset represents simulated assessment distributions for pipeline evaluation.
    """
    np.random.seed(42)
    num_samples = 600

    aptitude = np.random.normal(72, 14, num_samples).clip(30, 100)
    resume = np.random.normal(70, 13, num_samples).clip(35, 100)
    technical = np.random.normal(68, 15, num_samples).clip(25, 100)
    communication = np.random.normal(70, 14, num_samples).clip(30, 100)

    # Weighted composite score (Aptitude 20%, Resume 20%, Technical 40%, Communication 20%)
    composite = (0.20 * aptitude) + (0.20 * resume) + (0.40 * technical) + (0.20 * communication)
    
    # Class labels: 1 if composite >= 68 with slight realistic variance
    labels = []
    for c in composite:
        prob = 1 / (1 + np.exp(-(c - 68) / 3.5))
        labels.append(1 if np.random.rand() < prob else 0)

    df = pd.DataFrame({
        'aptitude_score': np.round(aptitude, 1),
        'resume_score': np.round(resume, 1),
        'technical_score': np.round(technical, 1),
        'communication_score': np.round(communication, 1),
        'result': labels
    })

    dataset_dir = BASE_DIR / 'dataset'
    dataset_dir.mkdir(exist_ok=True)
    df.to_csv(dataset_dir / 'candidate_performance.csv', index=False)
    print(f"Generated candidate performance dataset with {num_samples} records.")
    return df

def train_and_save_model():
    """Train and evaluate Random Forest Classifier vs Logistic Regression with comprehensive metrics."""
    csv_path = BASE_DIR / 'dataset' / 'candidate_performance.csv'
    if not csv_path.exists():
        df = generate_synthetic_dataset()
    else:
        df = pd.read_csv(csv_path)

    X = df[['aptitude_score', 'resume_score', 'technical_score', 'communication_score']]
    y = df['result']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Random Forest Classifier
    rf_model = RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    rf_pred = rf_model.predict(X_test_scaled)
    rf_probs = rf_model.predict_proba(X_test_scaled)[:, 1]

    rf_acc = accuracy_score(y_test, rf_pred)
    rf_prec = precision_score(y_test, rf_pred)
    rf_rec = recall_score(y_test, rf_pred)
    rf_f1 = f1_score(y_test, rf_pred)
    rf_auc = roc_auc_score(y_test, rf_probs)
    rf_cm = confusion_matrix(y_test, rf_pred).tolist()

    # 2. Logistic Regression
    lr_model = LogisticRegression(random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    lr_pred = lr_model.predict(X_test_scaled)
    lr_probs = lr_model.predict_proba(X_test_scaled)[:, 1]

    lr_acc = accuracy_score(y_test, lr_pred)
    lr_prec = precision_score(y_test, lr_pred)
    lr_rec = recall_score(y_test, lr_pred)
    lr_f1 = f1_score(y_test, lr_pred)
    lr_auc = roc_auc_score(y_test, lr_probs)
    lr_cm = confusion_matrix(y_test, lr_pred).tolist()

    print("=== Model Evaluation Comparison ===")
    print(f"Random Forest  -> Accuracy: {rf_acc*100:.2f}%, Precision: {rf_prec*100:.2f}%, Recall: {rf_rec*100:.2f}%, F1: {rf_f1*100:.2f}%, ROC-AUC: {rf_auc*100:.2f}%")
    print(f"Logistic Reg   -> Accuracy: {lr_acc*100:.2f}%, Precision: {lr_prec*100:.2f}%, Recall: {lr_rec*100:.2f}%, F1: {lr_f1*100:.2f}%, ROC-AUC: {lr_auc*100:.2f}%")

    if rf_f1 >= lr_f1:
        best_model = rf_model
        best_name = "Random Forest Classifier"
        metrics = {
            'model_name': best_name,
            'accuracy': round(rf_acc * 100, 2),
            'precision': round(rf_prec * 100, 2),
            'recall': round(rf_rec * 100, 2),
            'f1_score': round(rf_f1 * 100, 2),
            'roc_auc': round(rf_auc * 100, 2),
            'confusion_matrix': rf_cm,
            'disclaimer': 'The ML model is a prototype trained on simulated candidate performance data to demonstrate the complete machine learning pipeline.'
        }
    else:
        best_model = lr_model
        best_name = "Logistic Regression"
        metrics = {
            'model_name': best_name,
            'accuracy': round(lr_acc * 100, 2),
            'precision': round(lr_prec * 100, 2),
            'recall': round(lr_rec * 100, 2),
            'f1_score': round(lr_f1 * 100, 2),
            'roc_auc': round(lr_auc * 100, 2),
            'confusion_matrix': lr_cm,
            'disclaimer': 'The ML model is a prototype trained on simulated candidate performance data to demonstrate the complete machine learning pipeline.'
        }

    models_dir = BASE_DIR / 'models'
    models_dir.mkdir(exist_ok=True)

    joblib.dump(best_model, models_dir / 'performance_model.pkl')
    joblib.dump(scaler, models_dir / 'scaler.pkl')

    with open(models_dir / 'metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved best model ({best_name}) and evaluation metrics to {models_dir}")
    return best_model, scaler, metrics

if __name__ == '__main__':
    train_and_save_model()
