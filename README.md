# 🌿 EcoTrace — Carbon Footprint Predictor

**Mini Project 22CSE665 | Nitte Meenakshi Institute of Technology**  
**Department of Computer Science and Engineering | AY 2025–2026**

---

## Team
| Name |
|------|
| B S Bindushree |
| Vaibhav S Sollapure |
| Varshini G |
| Veenal Coutinho |


---

# 🚀 Features

- 🌍 Carbon footprint prediction
- 📊 Environmental impact analysis
- 🤖 Machine learning-based prediction system
- 📈 Data visualization dashboards
- 🧠 Feature importance analysis
- 🔍 User emission category classification
- 📉 Behavioral pattern analysis
- ⚡ Flask-based interactive web application
- 🌱 Sustainability awareness platform

---
## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Train models (only needed first time, models.pkl already included)
```bash
python model/train_model.py
```

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000          → Main Predictor
http://localhost:5000/dashboard → Analytics Dashboard
```

---
# 📂 Dataset Information

The dataset contains lifestyle-related attributes such as:

- Transportation mode
- Air travel frequency
- Diet type
- Energy source
- Shopping behavior
- Grocery expenditure
- Waste generation
- Energy efficiency

Dataset Source:
https://www.kaggle.com/datasets/dumanmesut/individual-carbon-footprint-calculation

---
## Dataset
**Source:** Kaggle — Individual Carbon Footprint Calculation  
**Records:** 10,000 real individuals  
**Target:** `CarbonEmission` (kg CO₂ per year)  
**Features used:** 16 (10 categorical + 6 numerical)

### Features
| Feature | Type | Description |
|---------|------|-------------|
| Body Type | Categorical | normal / overweight / obese / underweight |
| Sex | Categorical | male / female |
| Diet | Categorical | omnivore / pescatarian / vegetarian / vegan |
| How Often Shower | Categorical | daily / twice a day / more / less |
| Heating Energy Source | Categorical | coal / natural gas / electricity / wood |
| Transport | Categorical | private / public / walk/bicycle |
| Social Activity | Categorical | never / sometimes / often |
| Frequency of Traveling by Air | Categorical | never / rarely / frequently / very frequently |
| Waste Bag Size | Categorical | small / medium / large / extra large |
| Energy efficiency | Categorical | No / Sometimes / Yes |
| Monthly Grocery Bill | Numerical | $ per month |
| Vehicle Monthly Distance Km | Numerical | km per month |
| Waste Bag Weekly Count | Numerical | bags per week |
| How Long TV PC Daily Hour | Numerical | hours per day |
| How Many New Clothes Monthly | Numerical | items per month |
| How Long Internet Daily Hour | Numerical | hours per day |

---

## Model Performance (on real Kaggle data)
| Model | Metric | Score |
|-------|--------|-------|
| RF Regressor | R² | 0.7530 |
| RF Regressor | MAE | ~321 kg |
| RF Classifier | Accuracy | **77.40%** |
| DT Classifier | Accuracy | 71.95% |
| Linear Regression | R² | 0.5497 |

---

## Project Structure
```
carbon_footprint_predictor/
├── app.py                    # Flask backend
├── requirements.txt
├── README.md
├── data/
│   └── carbon_footprint_dataset.csv   # Real Kaggle dataset (10,000 rows)
├── model/
│   ├── train_model.py        # Training script
│   ├── models.pkl            # Pre-trained models (ready to run)
│   └── metrics.json          # Performance metrics
├── templates/
│   ├── index.html            # Predictor UI
│   └── dashboard.html        # Analytics dashboard
└── static/
    ├── css/style.css
    ├── css/dashboard.css
    ├── js/main.js
    └── js/dashboard.js
```

---

## Data Mining Techniques
| Technique | Algorithm | Purpose |
|-----------|-----------|---------|
| Regression | Random Forest | Predict exact CO₂ value |
| Regression | Linear Regression | Baseline regression model |
| Classification | Random Forest | Categorise Low/Medium/High |
| Classification | Decision Tree | Interpretable classifier |
| Clustering | K-Means (k=3) | Group users by lifestyle |

---

## References
- Kaggle Individual Carbon Footprint Dataset
- Han, J., Kamber, M., & Pei, J. (2011). *Data Mining: Concepts and Techniques*
- Pedregosa et al. (2011). *Scikit-learn: Machine Learning in Python*
- Breiman, L. (2001). *Random Forests. Machine Learning Journal*
- IPCC Climate Change Reports (Latest Edition)
