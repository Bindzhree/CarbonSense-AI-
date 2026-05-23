from flask import Flask, render_template, request, jsonify
import pickle, json, os
import numpy as np
import pandas as pd

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'model', 'models.pkl'), 'rb') as f:
    models = pickle.load(f)
with open(os.path.join(BASE_DIR, 'model', 'metrics.json'), 'r') as f:
    metrics = json.load(f)
df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'carbon_footprint_dataset.csv'))
df['emission_category'] = pd.cut(
    df['CarbonEmission'],
    bins=[0, 1500, 2500, 10000],
    labels=['Low', 'Medium', 'High']
)

rf_reg       = models['rf_regressor']
rf_clf       = models['rf_classifier']
scaler       = models['scaler']
encoders     = models['encoders']
label_enc    = models['label_encoder']
feature_cols = models['feature_cols']
thresholds   = models['thresholds']

OPTIONS = {
    'body_types':       ['normal', 'overweight', 'obese', 'underweight'],
    'sexes':            ['female', 'male'],
    'diets':            ['omnivore', 'pescatarian', 'vegetarian', 'vegan'],
    'shower_freqs':     ['daily', 'twice a day', 'more frequently', 'less frequently'],
    'heating_sources':  ['coal', 'natural gas', 'electricity', 'wood'],
    'transports':       ['private', 'public', 'walk/bicycle'],
    'social_activities':['never', 'sometimes', 'often'],
    'air_travel_freqs': ['never', 'rarely', 'frequently', 'very frequently'],
    'waste_bag_sizes':  ['small', 'medium', 'large', 'extra large'],
    'energy_efficiencies': ['No', 'Sometimes', 'Yes'],
}

CAT_COLS = [
    'Body Type', 'Sex', 'Diet', 'How Often Shower',
    'Heating Energy Source', 'Transport', 'Social Activity',
    'Frequency of Traveling by Air', 'Waste Bag Size', 'Energy efficiency'
]

def encode_and_scale(raw):
    enc = {}
    for col, val in zip(CAT_COLS, [
        raw['body_type'], raw['sex'], raw['diet'], raw['shower_freq'],
        raw['heating_source'], raw['transport'], raw['social_activity'],
        raw['air_travel_freq'], raw['waste_bag_size'], raw['energy_efficiency']
    ]):
        enc[col] = encoders[col].transform([val])[0]

    enc['Monthly Grocery Bill']       = float(raw['grocery_bill'])
    enc['Vehicle Monthly Distance Km']= float(raw['vehicle_km'])
    enc['Waste Bag Weekly Count']     = int(raw['waste_bag_count'])
    enc['How Long TV PC Daily Hour']  = float(raw['tv_pc_hours'])
    enc['How Many New Clothes Monthly']= int(raw['new_clothes'])
    enc['How Long Internet Daily Hour']= float(raw['internet_hours'])

    X = pd.DataFrame([[enc[c] for c in feature_cols]], columns=feature_cols)
    return scaler.transform(X)

def get_recommendations(raw):
    recs = []
    if raw['transport'] == 'private':
        recs.append({'icon':'🚌','title':'Switch to Public Transport',
                     'desc':'Private vehicles are the top CO₂ contributor. Public transport cuts emissions by up to 75%.','impact':'Very High Impact'})
    if raw['air_travel_freq'] in ['frequently','very frequently']:
        recs.append({'icon':'✈️','title':'Reduce Air Travel',
                     'desc':'Frequent flying significantly increases your footprint. Consider trains or video calls.','impact':'Very High Impact'})
    if raw['diet'] == 'omnivore':
        recs.append({'icon':'🥗','title':'Reduce Meat Consumption',
                     'desc':'Shifting toward vegetarian or pescatarian diet can cut food emissions by 30–50%.','impact':'High Impact'})
    if raw['heating_source'] in ['coal','natural gas']:
        recs.append({'icon':'☀️','title':'Switch to Cleaner Energy',
                     'desc':'Electricity or wood heating produces significantly fewer emissions than coal or gas.','impact':'High Impact'})
    if raw['energy_efficiency'] == 'No':
        recs.append({'icon':'💡','title':'Adopt Energy Efficiency',
                     'desc':'Using energy-efficient appliances and habits can cut home energy use by 20–30%.','impact':'Medium Impact'})
    if int(raw['new_clothes']) > 15:
        recs.append({'icon':'👕','title':'Buy Less Fast Fashion',
                     'desc':'Clothing production is highly carbon-intensive. Buy less, buy second-hand.','impact':'Medium Impact'})
    if raw['waste_bag_size'] in ['large','extra large']:
        recs.append({'icon':'♻️','title':'Reduce & Recycle Waste',
                     'desc':'Smaller waste output through composting and recycling reduces landfill emissions.','impact':'Low Impact'})
    if not recs:
        recs.append({'icon':'🌱','title':'Excellent Eco-Habits!',
                     'desc':'Your lifestyle is already low-impact. Spread the word and inspire others!','impact':'Community Impact'})
    return recs

def get_breakdown(raw):
    transport_map  = {'private':2500,'public':600,'walk/bicycle':50}
    diet_map       = {'omnivore':2000,'pescatarian':1500,'vegetarian':1000,'vegan':600}
    heating_map    = {'coal':1200,'natural gas':900,'electricity':500,'wood':400}
    air_map        = {'never':0,'rarely':400,'frequently':1200,'very frequently':2500}
    clothes_co2    = int(raw['new_clothes']) * 30
    grocery_co2    = int(float(raw['grocery_bill'])) * 2
    digital_co2    = (float(raw['tv_pc_hours']) + float(raw['internet_hours'])) * 30
    return {
        'Transport':  transport_map[raw['transport']],
        'Diet':       diet_map[raw['diet']],
        'Heating':    heating_map[raw['heating_source']],
        'Air Travel': air_map[raw['air_travel_freq']],
        'Clothing':   clothes_co2,
        'Groceries':  grocery_co2,
        'Digital':    round(digital_co2),
    }

@app.route('/')
def index():
    return render_template('index.html', options=OPTIONS)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        raw = request.get_json()
        X_sc = encode_and_scale(raw)

        co2_pred  = float(rf_reg.predict(X_sc)[0])
        cat_enc   = rf_clf.predict(X_sc)[0]
        cat_pred  = label_enc.inverse_transform([cat_enc])[0]
        proba     = rf_clf.predict_proba(X_sc)[0]
        percentile= float(np.sum(df['CarbonEmission'] < co2_pred) / len(df) * 100)

        return jsonify({
            'success':           True,
            'co2_prediction':    round(co2_pred, 2),
            'emission_category': cat_pred,
            'percentile':        round(percentile, 1),
            'probabilities':     {label_enc.classes_[i]: round(float(p)*100,1)
                                  for i,p in enumerate(proba)},
            'breakdown':         get_breakdown(raw),
            'recommendations':   get_recommendations(raw)
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', metrics=metrics)

@app.route('/api/metrics')
def api_metrics():
    return jsonify(metrics)

@app.route('/api/dataset-stats')
def dataset_stats():
    co2 = df['CarbonEmission']

    return jsonify({
        'total': int(len(df)),

        'mean_co2': float(round(co2.mean(), 2)),
        'median_co2': float(round(co2.median(), 2)),
        'min_co2': float(round(co2.min(), 2)),
        'max_co2': float(round(co2.max(), 2)),

        'emission_dist': {k: int(v) for k, v in df['emission_category'].value_counts().to_dict().items()}
                         if 'emission_category' in df.columns else {},

        'transport_dist': {k: int(v) for k, v in df['Transport'].value_counts().to_dict().items()},
        'diet_dist': {k: int(v) for k, v in df['Diet'].value_counts().to_dict().items()},

        'co2_by_diet': {k: float(v) for k, v in df.groupby('Diet')['CarbonEmission'].mean().round(2).to_dict().items()},
        'co2_by_transport': {k: float(v) for k, v in df.groupby('Transport')['CarbonEmission'].mean().round(2).to_dict().items()},
        'co2_by_heating': {k: float(v) for k, v in df.groupby('Heating Energy Source')['CarbonEmission'].mean().round(2).to_dict().items()},
        'co2_by_travel': {k: float(v) for k, v in df.groupby('Frequency of Traveling by Air')['CarbonEmission'].mean().round(2).to_dict().items()},
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)