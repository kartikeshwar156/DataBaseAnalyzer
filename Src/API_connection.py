import requests
import json
import os
import sqlite3
import pandas as pd


url = "https://api.arliai.com/v1/chat/completions"

API_URL = "https://www.alphavantage.co/query"
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "zomato.BSE",
    "outputsize": "full",
    "apikey": "WAGQE2A81MNIVJA7"
}

def extract(API_URL, params) -> dict:
    # API_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=CochinShip.BSE&outputsize=full&apikey=WAGQE2A81MNIVJA7"
    data = requests.get(API_URL, params=params).json()
    return data

def transform(data: dict) -> pd.DataFrame:
    time_series = data["Time Series (Daily)"]
    records = []

    for date, values in time_series.items():
        open_price = float(values["1. open"])
        high_price = float(values["2. high"])
        low_price = float(values["3. low"])
        close_price = float(values["4. close"])
        volume = int(values["5. volume"])
        avg_price = (open_price + close_price) / 2
        records.append([date, open_price, high_price,
                       low_price, close_price, volume, avg_price])

    df = pd.DataFrame(records, columns=[
                      "Date", "Open", "High", "Low", "Close", "Volume", "Avg Price"])
    return df

def load(df: pd.DataFrame, db_path)-> None:
    """ Load data in sqllite database
    """    
    conn=sqlite3.connect(db_path)
    table_name='new_stock_table'
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close
    
db_path = 'mystore.db'

data = extract(API_URL, params)
df = transform(data)
load(df, db_path)


new_con = sqlite3.connect('mystore.db')
new_cur = new_con.cursor()
res = new_cur.execute("SELECT * FROM new_stock_table")
print(res.fetchmany(size=20))
data = res.fetchmany(size=20)  # Fetch the rows
# Convert rows into a string
formatted_data = "\n".join([str(row) for row in data])
print(formatted_data)
print("this is formatted data")

headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer b3626de5-a5ce-4549-b233-d6f4430f3e1b"
}


def process_api_response(response):
    if response.status_code == 200:
        analysis_result = response.json()
        print_result = analysis_result['choices'][0]['message']['content']
        print("Analysis Result:",
              analysis_result['choices'][0]['message']['content'])
    else:
        print(
            f"Failed to call ArliAI API. Status Code: {response.status_code}")
        print("Response:", response.text)


def process_input(input_text, formatted_data):
    payload = json.dumps({
        "model": "Mistral-Nemo-12B-Instruct-2407",
        "messages": [
            #  {"role": "system", "content": "You are a helpful assistant."},
            #  {"role": "user", "content": "Hello!"},
            #  {"role": "assistant", "content": "Hi!, how can I help you today?"},
            {"role": "user", "content": f"{input_text}, \n\n{formatted_data}"},
        ],
        "repetition_penalty": 1.1,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 1024,
        "stream": False
    })
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    process_api_response(response)
    

while True:
    user_input = input("Enter something (type 'end' to stop): ")

    if user_input.lower() == "end":
        print("Loop ended. Goodbye!")
        break

    # Process the input using the function
    process_input(user_input, formatted_data)
