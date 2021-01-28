# Evaluation function and back-testing methods and simulations
import get_data as gd
import indicators as ind 
import random
import math
import matplotlib as mpl
import matplotlib.pyplot as plt

'''
Evaluate a symbol and decide buy/sell/sit overnight

RETURNS: buy, sell
- buy: how much money to invest in this symbol
- sell: how many shares to sell

INPUT:
- cash: amount of cash avaiable to invest on this symbol
- invested: the amount of shares of this symbol that we currently own
- bought_at: the price-per-share of this symbol when we last bought shares
- table: the table of data for this symbol 
'''
def evaluate_symbol(cash, invested, bought_at, table):
    # buy: how much money to invest in the symbol
    # sell: how many shares to sell
    buy = 0.0
    sell = 0.0

    # variables for indicators/prices
    macd = table['MACD']
    macd_hist = table['MACD_Hist']
    macd_signal = table['MACD_Signal']

    a_up = table['Aroon Up']
    a_down = table['Aroon Down']

    b_up = table['Real Upper Band']
    b_mid = table['Real Middle Band']
    b_low = table['Real Lower Band']
 
    obv = table['OBV']
    
    # calculations:
    # look for buy siganl when CCI moves from negative/near-zero to above 100
    if (invested == 0):
        #if (ind.cci(20, table) > 100) and (ind.cci(20, table[1:]) < 10):
         #   buy = cash
        if (a_up[0] > 70) and (a_down[0] < 30):
            buy = cash

    if (invested > 0):
        if (bought_at < ind.sma(4, 'close', table)) or (bought_at > ind.sma(2, 'high', table)):
            sell = invested

    return buy, sell
#end def 

'''
Simulate evaluation function over time. a.k.a. "backtesting".
Splits money evenly bewteen symbols and invests independently. 
Loops through each symbol and simulates whole time period.

RETURNS: the total percentage gained/lost after evaluating all symbols over 
         the time period  
INPUT: 
- list_syms: list of symbols to be looked at / invested in  
- a: start day 
- b: end day 
'''
def sim_past(list_syms, a, b):
    start_money = 100
    allowance = float(start_money) / float(len(list_syms))
    percents = dict.fromkeys(list_syms, 0.0)
    start = a
    end = b

    super_totals = [0.0] * (end-start)

    # set up chart 
    #x = range(end-start)
    #fig, axs = plt.subplots(2)

    #iterate through symbols:
    for symbol in list_syms:

        #set up this symbol's table
        table = gd.get_table(symbol)
        #print(symbol, len(table))
        if len(table) < (end):
            start = 0
            end = len(table) - 30
        table = table[start:end+30] # allows you to look 15 days back, on day one

        # set up variables
        cash = allowance
        invested = 0.0
        bought_at = 0.0
        buy = 0.0
        sell = 0.0
        # keep track of cash, owned shares, and closing price of each day
        money = [0.0] * (end-start)
        shares = [0.0] * (end-start)
        price = [0.0] * (end-start)

        i = 0
        # go through days. "day" counts down.
        for day in range(end-start, 0, -1):
            #simulate buy/sell at beginnning of day
            #buy 
            if buy > 0.0 :
                invested = invested + (float(buy) / table.iloc[day]['open'])
                cash = cash - float(buy)
                bought_at = table.iloc[day]['open']
                buy = 0.0
            #sell
            if sell > 0 :
                invested = invested - float(sell)
                cash = cash + (float(sell) * table.iloc[day]['open'])
                bought_at = 0.0
                sell = 0.0

            #evaluate and determine buy/sell for the morning 
            buy, sell = evaluate_symbol(cash, invested, bought_at, table[day:])
        
            # update lists keeping track
            money[i] = cash
            shares[i] = invested
            price[i] = table['close'][day]
            super_totals[i] += money[i] + (shares[i] * price[i])
            i += 1
        #end for

        #chart this symbol's journey, adjusted for sharing of initial cash
        totals = [(money[i] + (shares[i] * price[i])) * len(list_syms) for i in range(len(money))]
        #axs[0].plot(x, totals, ls='-', label=symbol+" total value")

        #evaluate cash + owned_shares*price at this point CLOSE PRICE
        percents[symbol] = cash + (invested * table['close'][0])

    #end for 
    # finalize the chart
    #axs[0].plot(x, super_totals, ls='-.', c='k', label="total value")
    #axs[0].legend(loc=6)
    #plt.savefig("multiple.png")

    # calculate statistics and return 
    tot_mon = sum(percents.values())
    t = 0.0
    for y in percents.values():
        t += y
    mean = t/len(list_syms)
    s = 0.0
    for x in percents.values():
        s += pow((x - mean), 2)
    stdev = 0.0
    if len(list_syms) == 1:
        stdev = 0
    else: 
        stdev = math.sqrt(s / (len(list_syms)-1))
    #print("Mean:", round(mean, 3), "| Std.Dev.:", round(stdev, 3))
    
    # plot histogram of individual gains/losses:

    #n, bins, patches = axs[1].hist(percents.values(), bins=10)
    #axs[1].xlabel("Gain/Loss (% of original investment)")
    #axs[1].ylabel("Frequency")
    #axs[1].title("Return of investment (%) after"+str(end-start)+"days, from "+str(len(list_syms))+" symbols.")
    #plt.savefig("sim_past.png")
    return super_totals[end-start-1] - 100
#end def

'''
Simulate evaluation function over time. a.k.a. "backtesting".
Only looks at one symbol and simulates over time period.
Prints two graphs to "one_symbol_detailed.png". One of total
value of assets (cash + value of owned shares), and one of the 
price of the symbol.

RETURNS: The percentage of money gained/lost after this simulation
INPUT: 
- symbol: list of symbols as strings to be considered for investment  
- a: start day 
- b: end day 
'''
def one_symbol_detailed(symbol, a, b):
    start = a
    end = b

    totals = [0.0] * (end-start)

    # set up chart 
    plt.figure(0)
    x = range(end-start)
    fig, axs = plt.subplots(2)
    
    #set up this symbol's table
    table = gd.get_table(symbol)
    #print(symbol, len(table))
    if len(table) < (end):
        start = 0
        end = len(table) - 30
    table = table[start:end+30] # allows you to look 30 days back, on day one

    # set up variables
    cash = 100
    invested = 0.0
    bought_at = 0.0
    buy = 0.0
    sell = 0.0
    # keep track of cash, owned shares, and prices (hig, low, typical) of each day
    money = [0.0] * (end-start)
    shares = [0.0] * (end-start)
    high = [0.0] * (end-start)
    low = [0.0] * (end-start)
    tp = [0.0] * (end-start)

    i = 0
    # go through days. "day" counts down.
    for day in range(end-start, 0, -1):
        #simulate buy/sell at beginnning of day
        #buy 
        if buy > 0 :
            invested = invested + (float(buy) / table.iloc[day]['open'])
            cash = cash - float(buy)
            bought_at = table.iloc[day]['open']
            buy = 0.0
        #sell
        if sell > 0 :
            invested = invested - float(sell)
            cash = cash + (float(sell) * table.iloc[day]['open'])
            bought_at = 0.0

        #evaluate and determine buy/sell for the morning 
        buy, sell = evaluate_symbol(cash, invested, bought_at, table[day:])
    
        # update lists keeping track
        money[i] = cash
        shares[i] = invested
        high[i] = table['high'][day]
        low[i] = table['low'][day]
        tp[i] = (high[i] + low[i] + table['close'][day]) / 3
        totals[i] += money[i] + (shares[i] * tp[i])
        i += 1
    #end for
    
    axs[0].plot(x, totals, ls='-')

    #axs[0].title(label="Cash + value of owned shares by day")
    #chart the price of the stock
    axs[1].plot(x, high, ls="-")
    axs[1].plot(x, low, ls="-")
    axs[1].plot(x, tp, ls="-")
    #axs[1].title(label="Price of "+symbol)

    plt.savefig("one_symbol_detailed.png")
    plt.show()

    #return the percentage of money gained/lost after this simulation
    return totals[len(totals)-1] - 100
#end def

'''
Run evaluation function on list of symbols for a certain amount of trials,
where each trial uses a random stretch of "days" trading days, and 
present statistics about the results.
Prints a histogram of the trials' results to "experiment.png"
RETURNS: data, mean, stdev
- data: List of results of each trial. A result is the percentage gained/lost
- mean: average of sample
- stdev: standard deviation of sample 
INPUT:
- ls: list of symbols as strings
- trials: number of trials to complete
- days: the number of trading days
'''
def rand_sims(ls, trials, days): 
    data = [0.0] * trials

    for i in range(trials): 
        a = random.randint(0, 700-days)
        pct = sim_past(ls, a, a + days)
        data[i] = pct
        print("Trial", i+1, "complete")
    #end for 
    # statistics:
    mean = float(sum(data)) / float(len(data))
    s = 0.0
    for x in data:
        s += pow((x-mean), 2)
    #end for
    var = 0.0 
    if (trials == 1):
        var = 0.0
    else: 
        var = s / (trials - 1)
    stdev = math.sqrt(var)

    # plot  data 
    plt.figure(1)
    n, bins, patches=plt.hist(data, bins=10)
    plt.xlabel("Gain/Loss (% of original investment)")
    plt.ylabel("Frequency")
    plt.title(str(trials)+" trials; Return of investment (%) after"+str(days)+"days.")
    plt.savefig("experiment.png")
    plt.show()

    return data, mean, stdev
#end def 

