import requests

import pandas as pd

from sqlalchemy import create_engine

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
