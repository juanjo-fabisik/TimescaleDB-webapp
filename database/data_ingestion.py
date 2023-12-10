import csv
import pandas as pd
import config 
import psycopg2
from pgcopy import CopyManager
import numpy as np


conn = psycopg2.connect(database=config.DB_NAME, 
                            host=config.DB_HOST, 
                            user=config.DB_USER, 
                            password=config.DB_PASS, 
                            port=config.DB_PORT)


# read dataset from disk
def read_dataset(dataset_filename):
    df = pd.read_csv(dataset_filename) 
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df = df.rename(columns={'timestamp': 'time_hour', 
                            'close': 'price_close', 
                            'high': 'price_high',
                            'low': 'price_low',
                            'volume': 'trading_volume'}
                            )

    symbols = df["symbol"].unique()
    
    for symbol in symbols:
        # create a new column: price open, by copying the price close from the previous data point.
        df.loc[df['symbol'] == symbol, 'price_open'] = df.loc[df['symbol'] == symbol, 'price_close'].shift(1)

    df = df.dropna()
    return [row for row in df.itertuples(index=False, name=None)] 


def main():

    print("Reading dataset...")
    crypto_dataset = read_dataset("raw/trades.csv")
    
    print('Inserting data...')
    table_name = "dataset_by_hour"
    columns = ('time_hour', 'symbol', 'price_high', 'price_low','price_close', 'trading_volume', 'price_open')
    mgr = CopyManager(conn, table_name, columns)
    mgr.copy(crypto_dataset)
    conn.commit()


if __name__ == '__main__':
    main()