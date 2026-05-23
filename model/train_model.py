import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, mean_absolute_error,
                              r2_score, confusion_matrix)
from sklearn.cluster import KMeans
import pickle, os, json

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'carbon_footprint_dataset.csv')

df = pd.read_csv(DATA_PATH)
print("Dataset loaded:", df.shape)

CAT_FEATURES = [
    'Body Type', 'Sex', 'Diet', 'How Often Shower',
    'Heating Energy Source', 'Transport', 'Social Activity',
    'Frequency of Traveling by Air', 'Waste Bag Size', 'Energy efficiency'
]
NUM_FEATURES = [
    'Monthly Grocery Bill', 'Vehicle Monthly Distance Km',
    'Waste Bag Weekly Count', 'How Long TV PC Daily Hour',
    'How Many New Clothes Monthly', 'How Long Internet Daily Hour'
]
TARGET_COL   = 'CarbonEmission'
FEATURE_COLS = CAT_FEATURES + NUM_FEATURES

df = df[FEATURE_COLS + [TARGET_COL]].dropna()
print("After dropna:", df.shape)

p33 = df[TARGET_COL].quantile(0.33)
p66 = df[TARGET_COL].quantile(0.66)
print(f"Category thresholds → Low ≤{p33:.0f}  Medium ≤{p66:.0f}  High >{p66:.0f}")

def emission_cat(v):
    if v <= p33:  return 'Low'
    if v <= p66:  return 'Medium'
    return 'High'

df['emission_category'] = df[TARGET_COL].apply(emission_cat)
print(df['emission_category'].value_counts())

encoders = {}
df_enc = df.copy()
for col in CAT_FEATURES:
    le = LabelEncoder()
    df_enc[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

label_enc = LabelEncoder()
df_enc['emission_category_enc'] = label_enc.fit_transform(df['emission_category'])
encoders['emission_category'] = label_enc

X     = df_enc[FEATURE_COLS]
y_reg = df_enc[TARGET_COL]
y_clf = df_enc['emission_category_enc']

X_train, X_test, yr_train, yr_test, yc_train, yc_test = train_test_split(
    X, y_reg, y_clf, test_size=0.2, random_state=42)

scaler     = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

rf_reg = RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1)
rf_reg.fit(X_train_sc, yr_train)

lin_reg = LinearRegression()
lin_reg.fit(X_train_sc, yr_train)

rf_clf = RandomForestClassifier(n_estimators=150, random_state=42,
                                 class_weight='balanced', n_jobs=-1)
rf_clf.fit(X_train_sc, yc_train)

dt_clf = DecisionTreeClassifier(max_depth=10, random_state=42, class_weight='balanced')
dt_clf.fit(X_train_sc, yc_train)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(X_train_sc)

yr_pred     = rf_reg.predict(X_test_sc)
yr_pred_lin = lin_reg.predict(X_test_sc)
yc_pred     = rf_clf.predict(X_test_sc)
yc_pred_dt  = dt_clf.predict(X_test_sc)

mae    = mean_absolute_error(yr_test, yr_pred)
r2     = r2_score(yr_test, yr_pred)
acc    = accuracy_score(yc_test, yc_pred)
acc_dt = accuracy_score(yc_test, yc_pred_dt)
fi     = pd.Series(rf_reg.feature_importances_,
                   index=FEATURE_COLS).sort_values(ascending=False)

print(f"\nRF Regression  → MAE: {mae:.2f}  R²: {r2:.4f}")
print(f"Lin Regression → MAE: {mean_absolute_error(yr_test,yr_pred_lin):.2f}  R²: {r2_score(yr_test,yr_pred_lin):.4f}")
print(f"RF Classifier  → Accuracy: {acc*100:.2f}%")
print(f"DT Classifier  → Accuracy: {acc_dt*100:.2f}%")
print("\nTop Features:\n", fi.head(8))

models_bundle = {
    'rf_regressor':     rf_reg,
    'linear_regressor': lin_reg,
    'rf_classifier':    rf_clf,
    'dt_classifier':    dt_clf,
    'kmeans':           kmeans,
    'scaler':           scaler,
    'encoders':         encoders,
    'feature_cols':     FEATURE_COLS,
    'label_encoder':    label_enc,
    'thresholds':       {'low': float(p33), 'medium': float(p66)}
}
with open(os.path.join(BASE_DIR, 'models.pkl'), 'wb') as f:
    pickle.dump(models_bundle, f)

metrics = {
    'rf_regression':       {'mae': round(mae,2), 'r2': round(r2,4)},
    'linear_regression':   {'mae': round(mean_absolute_error(yr_test,yr_pred_lin),2),
                            'r2':  round(r2_score(yr_test,yr_pred_lin),4)},
    'rf_classification':   {'accuracy': round(acc*100,2)},
    'dt_classification':   {'accuracy': round(acc_dt*100,2)},
    'feature_importance':  fi.round(4).to_dict(),
    'confusion_matrix':    confusion_matrix(yc_test, yc_pred).tolist(),
    'class_names':         list(label_enc.classes_),
    'train_size':          len(X_train),
    'test_size':           len(X_test),
    'total_records':       len(df),
    'emission_distribution': df['emission_category'].value_counts().to_dict()
}
with open(os.path.join(BASE_DIR, 'metrics.json'), 'w') as f:
    json.dump(metrics, f, indent=2)

print("\nAll models and metrics saved successfully!")
