"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import datetime as dt
import os
import math
from util import get_data, plot_data

def compute_portvals(orders_file = "./orders/orders.csv", start_val = 1000000):
    orders = pd.read_csv(orders_file, index_col = 'Date', parse_dates = True).sort_index()
    start_date = orders.index[0]
    end_date = orders.index[-1]
    symbols = []
    for symbol in orders['Symbol']:
        if symbol not in symbols:
            symbols.append(symbol)
    df_prices = get_data(symbols, pd.date_range(start_date, end_date), addSPY=False).dropna()
    df_prices['Cash'] = np.ones(len(df_prices.index))
    df_trades = df_prices * 0.0
    for i in range(len(orders.index)):
        symb = orders.ix[i][0]
        oper = orders.ix[i][1]
        shares = orders.ix[i][2]
        date = orders.index[i]
        if oper == 'BUY':
            df_trades.ix[date][symb] += shares
            df_trades.ix[date]['Cash'] -= shares * df_prices.ix[date][symb]
        if oper == 'SELL':
            df_trades.ix[date][symb] -= shares
            df_trades.ix[date]['Cash'] += shares * df_prices.ix[date][symb]
    leverage = True
    while(leverage):
        leverage = False
        df_holdings = df_trades.copy(deep=True)
        df_holdings.ix[0][-1] += start_val
        for i in range(1, len(df_holdings.index)):
            for j in range(len(df_holdings.ix[i])):
                df_holdings.ix[i][j] += df_holdings.ix[i-1][j] 
        df_values = df_prices * df_holdings
        for date in orders.index:
            longs = []
            shorts = []
            for i in range(len(df_values.ix[date])-1):
                value = df_values.ix[date][i]
                if value > 0:
                    longs.append(value)
                elif value < 0:
                    shorts.append(value)
            lev = (sum(longs) - sum(shorts)) / (sum(longs) + sum(shorts) + df_values.ix[date][-1])            
            if lev > 10.0:
                df_trades.ix[date] = np.zeros(len(df_trades.ix[date]))
                leverage = True
                break
    portvals = df_values.sum(axis=1)
    return portvals
    
def analysis(portvals):
    dr = portvals/portvals.shift(1) - 1
    dr = dr.ix[1:]
    cr = portvals.ix[-1] / portvals[0] - 1
    adr = dr.mean()
    sddr = dr.std()
    sr = math.sqrt(252) * adr /sddr
    return cr, adr, sddr, sr

def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters

    of = "./orders/orders.csv"
    sv = 10000

    # Process orders
    portvals = compute_portvals(orders_file = of, start_val = sv)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]] # just get the first column
    else:
        "warning, code did not return a DataFrame"
    
    # Get portfolio stats
    # Here we just fake the data. you should use your code from previous assignments.
    start_date = portvals.index[0]
    end_date = portvals.index[-1]
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = analysis(portvals)
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]

    # Compare portfolio against $SPX
    print "Date Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of SPY : {}".format(sharpe_ratio_SPY)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of SPY : {}".format(cum_ret_SPY)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of SPY : {}".format(std_daily_ret_SPY)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of SPY : {}".format(avg_daily_ret_SPY)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

if __name__ == "__main__":
    test_code()
