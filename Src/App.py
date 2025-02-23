from flask import Flask, request, jsonify
import requests
import json
import sqlite3
import pandas as pd
from flask_cors import CORS  # Import CORS
# CORS stands for Cross Origin Requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# External API endpoints
ARLIAI_URL = "https://api.arliai.com/v1/chat/completions"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

# Alpha Vantage API parameters
API_PARAMS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "zomato.BSE",
    "outputsize": "full",
    "apikey": "WAGQE2A81MNIVJA7"
}

# Headers for the AI API
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer b3626de5-a5ce-4549-b233-d6f4430f3e1b"
}

DB_PATH = "mystore.db"

# Function to fetch stock data
def extract(api_url, params):
    data = requests.get(api_url, params=params).json()
    return data

# Transform stock data into a DataFrame
def transform(data):
    time_series = data.get("Time Series (Daily)", {})
    records = []

    for date, values in time_series.items():
        records.append([
            date,
            float(values["1. open"]),
            float(values["2. high"]),
            float(values["3. low"]),
            float(values["4. close"]),
            int(values["5. volume"]),
            (float(values["1. open"]) + float(values["4. close"])) / 2  # Avg Price
        ])

    return pd.DataFrame(records, columns=["Date", "Open", "High", "Low", "Close", "Volume", "Avg Price"])

# Load data into SQLite database
def load(df, db_path):
    conn = sqlite3.connect(db_path)
    df.to_sql('new_stock_table', conn, if_exists='replace', index=False)
    conn.close()

# Fetch the latest stock data
data = extract(ALPHA_VANTAGE_URL, API_PARAMS)
df = transform(data)
load(df, DB_PATH)

# API Route to Handle Queries
@app.route('/query', methods=['POST'])
def handle_query():
    user_query = request.json.get("query")
    
    # Fetch latest stock data from the database
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM new_stock_table LIMIT 20")  # Fetching sample data
    stock_data = cur.fetchall()
    conn.close()
    
    # Format stock data for AI API
    formatted_data = "\n".join([str(row) for row in stock_data])

    # AI API Request Payload
    payload = json.dumps({
        "model": "Mistral-Nemo-12B-Instruct-2407",
        "messages": [{"role": "user", "content": f"{user_query}, \n\n{formatted_data}"}],
        "repetition_penalty": 1.1,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 1024,
        "stream": False
    })

    # Call AI API
    response = requests.post(ARLIAI_URL, headers=HEADERS, data=payload)

    # Return AI response to frontend
    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        return jsonify({"query": user_query, "response": ai_response})
    else:
        return jsonify({"error": "AI API request failed", "details": response.text}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(port=8080)
