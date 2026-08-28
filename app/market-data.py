import requests
import os
from dotenv import load_dotenv
import json
import yfinance as yf

load_dotenv()
# av_api_key = os.getenv("AV_API_KEY")

# url = f'https://www.alphavantage.co/query?function=REALTIME_BULK_QUOTES&symbol=MSFT,AAPL,IBM&apikey={av_api_key}'
# Define the ticker symbol
ticker_symbol = "AAPL"

# Create a Ticker object
ticker = yf.Ticker(ticker_symbol)

# Fetch historical market data
historical_data = ticker.history(period="1y")  # data for the last year
print("Historical Data:")
print(historical_data)

# Fetch basic financials
financials = ticker.financials
print("\nFinancials:")
print(financials)

# Fetch stock actions like dividends and splits
actions = ticker.actions
print("\nStock Actions:")
print(actions)

# parsed = json.loads(data)
    
# print(json.dumps(parsed, index=4))

# print(data)
