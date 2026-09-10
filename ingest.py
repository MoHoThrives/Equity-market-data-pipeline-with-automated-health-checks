import os
import pyodbc
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

TICKERS = ['MSFT', 'AAPL', 'GOOG', 'NVDA', 'AMD', 
               'SYY', 'F', 'PLUG', 'SOFI', 'TSLA', 'SMCI', 
               'AMZN', 'RIG', 'CHWY', 'CRWV', 'AMC', 'UBER',
               'HPE', 'VZ']


def get_connection():
    sa_password = os.environ["MSSQL_SA_PASSWORD"]
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=mssql-db,1433;"
        "DATABASE=MarketData;"
        "UID=sa;"
        f"PWD={sa_password};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


def get_or_create_security(cursor, ticker):
    cursor.execute("SELECT security_id FROM securities WHERE ticker = ?", ticker)
    row = cursor.fetchone()
    if row:
        return row.security_id

    info = yf.Ticker(ticker).info
    name = info.get("longName", ticker)
    sector = info.get("sector")

    cursor.execute(
        "INSERT INTO securities (ticker, name, sector) OUTPUT INSERTED.security_id VALUES (?, ?, ?)",
        ticker, name, sector
    )
    return cursor.fetchone().security_id


def fetch_and_process(ticker):
    df = yf.Ticker(ticker).history(period="1y", interval="1d")
    if df.empty:
        return None

    df = df.reset_index().sort_values("Date")
    df["daily_return"] = df["Close"].pct_change()
    df["moving_avg_50d"] = df["Close"].rolling(window=50).mean()
    df["rolling_volatility"] = df["daily_return"].rolling(window=50).std()
    df = df.astype(object).where(pd.notnull(df), None)
    return df


def insert_prices(cursor, security_id, df):
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO prices (security_id, trade_date, open_price, high_price, low_price, close_price, volume, daily_return, moving_avg_50d, rolling_volatility) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            security_id, row["Date"], row["Open"], row["High"], row["Low"], row["Close"],
            row["Volume"], row["daily_return"], row["moving_avg_50d"], row["rolling_volatility"]
        )


def main():
    conn = get_connection()
    cursor = conn.cursor()

    for ticker in TICKERS:
        print(f"Processing {ticker}...")
        df = fetch_and_process(ticker)
        if df is None:
            print(f"WARNING: no data returned for {ticker}")
            continue

        security_id = get_or_create_security(cursor, ticker)
        insert_prices(cursor, security_id, df)

    conn.commit()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()