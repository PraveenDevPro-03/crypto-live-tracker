import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# Google Sheets API Authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("your_credentials.json", SCOPE)
CLIENT = gspread.authorize(CREDS)


SPREADSHEET = CLIENT.open("Crypto Live Data")  

def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50, 
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def analyze_data(data):
    df = pd.DataFrame(data, columns=["name", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"])
    df.columns = ["Cryptocurrency Name", "Symbol", "Current Price (USD)", "Market Cap", "24h Trading Volume", "Price Change (24h %)"]

    top_5 = df.nlargest(5, "Market Cap")[["Cryptocurrency Name", "Market Cap"]]

  
    avg_price = df["Current Price (USD)"].mean()

  
    max_change = df.loc[df["Price Change (24h %)"].idxmax()]
    min_change = df.loc[df["Price Change (24h %)"].idxmin()]

    return df, top_5, avg_price, max_change, min_change


def update_google_sheets(df):
    worksheet = SPREADSHEET.get_worksheet(0)  
    worksheet.clear()  
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())  
    print(" Google Sheet Updated!")

def main():
    while True:
        print("Fetching Live Crypto Data...")
        data = fetch_crypto_data()
        df, top_5, avg_price, max_change, min_change = analyze_data(data)

        print("Updating Google Sheets...")
        update_google_sheets(df)

        print("Next update in 5 minutes...")
        time.sleep(300)  
if __name__ == "__main__":
    main()
