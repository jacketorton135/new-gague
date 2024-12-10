from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# CSV URLs
BMI_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTbj3f0rhEu2aCljm1AgkPiaqU7XLGfLUfmL_3NVClYABWXmarViEg1RSE4Q9St0YG_rR74VZyNh7MF/pub?output=csv'
ENV_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS5C_o47POhPXTZEgq40budOJB1ygTTZx9D_086I-ZbHfApFPZB_Ra5Xi09Qu6hxzk9_QXJ-7-QFoKD/pub?output=csv'
HEARTBEAT_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSULVwFdSh9_HuIJe1dWPae-jzcQYsyYb5DuRfXHtDenUlr1oSYTRr-AQ-aMthcCsNRTcVIbvmt_7qJ/pub?output=csv'

def load_csv(url):
    return pd.read_csv(url)

@app.route('/')
def index():
    # Load CSV data
    bmi_df = load_csv(BMI_CSV_URL)
    env_df = load_csv(ENV_CSV_URL)
    heartbeat_df = load_csv(HEARTBEAT_CSV_URL)
    
    # Combine data
    latest_bmi = bmi_df['bmi'].iloc[-1]
    latest_env = env_df.iloc[-1]
    latest_heartbeat = heartbeat_df['heartbeat'].iloc[-1]
    
    latest_data = {
        'temperature': latest_env['temperature'],
        'humidity': latest_env['humidity'],
        'bodyTemperature': latest_env['bodyTemperature'],
        'heartbeat': latest_heartbeat,
        'bmi': latest_bmi
    }
    
    # Prepare historical data
    historical_data = pd.concat([bmi_df, env_df[['temperature', 'humidity', 'bodyTemperature']], heartbeat_df[['heartbeat']]], axis=1).to_dict(orient='records')

    return render_template('index.html', data=latest_data, historical_data=historical_data)

@app.route('/api/data')
def api_data():
    bmi_df = load_csv(BMI_CSV_URL)
    env_df = load_csv(ENV_CSV_URL)
    heartbeat_df = load_csv(HEARTBEAT_CSV_URL)
    
    historical_data = pd.concat([bmi_df, env_df[['temperature', 'humidity', 'bodyTemperature']], heartbeat_df[['heartbeat']]], axis=1).to_dict(orient='records')
    return jsonify(historical_data)

if __name__ == '__main__':
    app.run(debug=True)


