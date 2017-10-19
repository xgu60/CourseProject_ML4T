"""MC1-P2: Optimize a portfolio."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import scipy.optimize as spo
import math
from util import get_data, plot_data


# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def optimize_portfolio(sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), \
    syms=['GOOG','AAPL','GLD','XOM'], gen_plot=False):

    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # find the allocations for the optimal portfolio
    # note that the values here ARE NOT meant to be correct for a test case
    def r_sharpratio(allocs):
        return analysis(prices, allocs)[3] * (-1)
    
    xGuess = np.ones(len(syms)) / float(len(syms))
    
    bs = [(0, 1) for i in range(len(syms))]
    cs = ({ 'type': 'eq', 'fun': lambda x: 1.0 - np.sum(x) })
          
    allocs = spo.minimize(r_sharpratio, xGuess, method = 'SLSQP', bounds = bs, constraints = cs)
    
    cr, adr, sddr, sr = analysis(prices, allocs.x)

    # Get daily portfolio value
    port_val = prices_SPY / prices_SPY.ix[0] # add code here to compute daily portfolio values
    port_val2 = (prices / prices.ix[0] * allocs.x).sum(axis = 1)
    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        df = pd.concat([port_val2, port_val], keys=['Portfolio', 'SPY'], axis=1)
        plot_data(df, title="Daily Portfolio Value and SPY", xlabel="Date", ylabel="Price")

    return allocs.x, cr, adr, sddr, sr

def analysis(prices, allocs):      

    # Get daily portfolio value
    port_val2 = prices / prices.ix[0] * allocs 
    
    # Get portfolio statistics (note: std_daily_ret = volatility)
    # add code here to compute stats
    vs = port_val2.sum(axis = 1)
    dr = vs/vs.shift(1) - 1
    dr = dr.ix[1:]
    cr = vs.ix[-1] - 1
    adr = dr.mean()
    sddr = dr.std()
    sr = math.sqrt(252) * adr / sddr

    return [cr, adr, sddr, sr]


if __name__ == "__main__":
    # This code WILL NOT be tested by the auto grader
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!

    start_date = dt.datetime(2005,12,1)
    end_date = dt.datetime(2006,05,31)
    symbols = ['YHOO', 'HPQ', 'GLD', 'HNZ']

    # Assess the portfolio
    allocations, cr, adr, sddr, sr = optimize_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        gen_plot = False)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocations
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr
