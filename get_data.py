# Functions to retrieve data (prices, technical indicators) and save them to a 
# file as a Pandas DataFrame, and load the DataFrame ffrom a file to memory.
# Gathers data by polling the AlphaVantage API.
import sys
import numpy as np
from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time 

apikey = #Alpha Vantage API key here (free to obtain)
urlbase = "https://www.alphavantage.co/query?"

'''
Retrieve data from API request and save the dataframe as "table_<symbol>.pkl"
contains: prices (open, high, low, close), OBV, AROON, MACD, Bollinger Bands
All periods are DAILY
INPUT:
- symbol: a string of the stock symbol for which to get data
'''
def save_table (symbol):

    #query prices 
    url = urlbase+"function=TIME_SERIES_DAILY&symbol="+symbol+"&outputsize=full&apikey="+apikey
    r = requests.get(url).json()
    # into dataframe
    df = pd.DataFrame(r['Time Series (Daily)']).transpose()
    # rename price columns 
    df.columns = ['open', 'high', 'low', 'close', 'volume']

    # Query Obv
    url = urlbase+"function=OBV&symbol="+symbol+"&interval=daily&apikey="+apikey
    r = requests.get(url).json()
    #into dataframe 
    df1 = pd.DataFrame(r['Technical Analysis: OBV']).transpose()
    # Merge dataframes 
    df = df.merge(df1, left_index=True, right_index=True)

    # Query Aroon 
    url = urlbase + "function=AROON&symbol="+symbol+"&interval=daily&time_period=14&apikey="+apikey
    r = requests.get(url).json()
    df1 = pd.DataFrame(r['Technical Analysis: AROON']).transpose()
    # Merge dataframes 
    df = df.merge(df1, left_index=True, right_index=True)

    # Query MACD
    url = urlbase + "function=MACD&symbol="+symbol+"&interval=daily&series_type=low&apikey="+apikey
    r = requests.get(url).json()
    df1 = pd.DataFrame(r['Technical Analysis: MACD']).transpose()
    # Merge dataframes 
    df = df.merge(df1, left_index=True, right_index=True)

    # Query Bollinger Bands
    url = urlbase + "function=BBANDS&symbol="+symbol+"&interval=daily&time_period=20&series_type=low&apikey="+apikey
    r = requests.get(url).json()
    df1 = pd.DataFrame(r['Technical Analysis: BBANDS']).transpose()
    # Merge dataframes 
    df = df.merge(df1, left_index=True, right_index=True)

    # convert values to floats 
    for col in df.columns:
        df[col] = df[col].astype(float)
    #end for 

    # Save dataframe to file
    fname = "table_" + symbol + ".pkl"
    df.to_pickle(fname)
    print("Successfully saved table for "+symbol)
#end def 
'''
Loads dataframe of [Prices, OBV, AROON, MACD, Bollinger Bands] for <symbol>
INPUT:
- symbol: a string of the stock symbol for which to get data
OUTPUT:
- Pandas DataFrame of [Prices, OBV, AROON, MACD, Bollinger Bands] for <symbol>
'''
def get_table(symbol):
    fname = "table_" + symbol + ".pkl"
    #print("Successfully loaded table for "+symbol)
    return pd.read_pickle(fname)
#end def 

