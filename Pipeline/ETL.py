import requests

import pandas as pd

from sqlalchemy import create_engine

import sqlite3

import os

import subprocess


# db_path = "../Database/my_stok_data.db"

# subprocess.run(f'icacls "{db_path}" /grant Everyone:F', shell=True)


# if os.path.exists(db_path):
#     os.chmod(db_path, 0o777)  # Read & Write for everyone
#     print(f"Permissions updated for {db_path}")
# else:
#     print("Database file not found!")

api_key = "WAGQE2A81MNIVJA7"
API_URL = "https://www.alphavantage.co/query"
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "zomato.BSE",
    "outputsize": "full",
    "apikey": "WAGQE2A81MNIVJA7"
}


def extract() -> dict:
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

def load(df: pd.DataFrame)-> None:
    """ Load data in sqllite database
    """
    
    # disk_engine = create_engine('sqlite:///../my_stok_data2.db')
    db_path='my_stok_data2.db'
    conn=sqlite3.connect(db_path)
    table_name='new_stock_table'
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    # name of the table is kept 'stock_data'
    # df.to_sql('stock_data2', disk_engine, if_exists='replace')
    
# loading the data by calling the functions in their respective sequesnce
data = extract()
df = transform(data)
load(df)