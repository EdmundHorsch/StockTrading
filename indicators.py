# Function to calculate variouis technical indicators based on a symbol's 
# price data
import random
import math
import numpy as np
import pandas as pd
import get_data as gd

'''
Simple Moving Average

RETURN: the simple moving avg of the past "days" days
INPUT: 
- days: for moving average
- type: price type (high, low, close, open)
- table: table of data to pull from
'''
def sma(days, type, table):
    s = 0.0
    for i in range(days):
        s += table[type][i]
    return s / days
#end def 

''' 
Commodity Channel Index (CCI)
RETURN: the CCI based on the given table
INPUT: 
- time period (n): number of past days to use in the calculation
- table: table of prices for a symbol
'''
def cci(n, table):
    #uses this method,but could define tp as todays TP
    high = max(table['high'][:n])
    low = min(table['low'][:n])
    tp = (high + low + table['close'][0]) / 3.0
    
    tps = [0.0] * n
    # calculate average typical price over last n days 
    for i in range(n):
        tps[i] = (table['high'][i] + table['low'][i] + table['close'][i]) / 3.0
    #end for 
    ma = sum(tps) / float(n) 

    md_s = [0.0] * n
    for i in range(n):
        md_s[i] = abs(tps[i] - ma)
        #print(md_s)
    md = sum(md_s) / float(n)

    if (md == 0):
        #print("n=",n,"| md_s=", md_s, " | tps=", tps,"\n", table.iloc[:n])
        return (tp - ma) / 0.001

    #print(tp, ma, md)
    return (tp - ma) / (0.015 * md)
#end def 

'''
Calculates the RSI given the table and period
RETURN: RSI value
INPUT:
- n: time period. number of past days to use in the calculation
- table: table of prices for a symbol
'''
def rsi(n, table):
    up = [0.0] * n
    dn = [0.0] * n
    #up and down bars 
    for i in range(n):
        if table['close'][i] > table['close'][i+1] :
            up[i] = table['close'][i] - table['close'][i+1]
            dn[i] = 0.0
        else:
            up[i] = 0.0
            dn[i] = table['close'][i+1] - table['close'][i]
    
    # simple moving average:
    up_avg = sum(up) / float(n)
    dn_avg = sum(dn) / float(n)
    #exponential moving average 
    up_avg = ema(up, n)
    dn_avg = ema(dn, n)
    #wilder's smoothing method
    up_avg = wilders_ema(up, n)
    dn_avg = wilders_ema(dn, n)
    
    #relative strength:
    rs = up_avg / dn_avg
    return 100.0 - (100.0 / (1.0 + rs))

'''
Helper function for RSI function.  Calculates the exponential moving average 
of a list based on last n days 
RETURN: exponential moving average 
INPUT:
- ls: list of prices (descending in recency)
- n: number of days to consider in the moving average 
'''
def ema(ls, n):
    if n == 1:
        return ls[0]
    a = 2.0 / (n + 1.0)
    return (ls[0] * a) + ((1-a) * ema(ls[1:], n-1))
#end def 

'''
Helper function for RSI function.  Calculates the exponential moving average 
of a list based on last n days, using Wilder's smoothing 
RETURN: exponential moving average 
INPUT:
- ls: list of prices (descending in recency)
- n: number of days to consider in the moving average 
'''
# exponential moving average of last n elements. for n >= 2
def wilders_ema(ls, n):
    if n == 1:
        return ls[0]
    a = 1.0 / n
    return (ls[0] * a) + ((1-a) * ema(ls[1:], n-1))
#end def 
