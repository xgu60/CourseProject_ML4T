"""MC1-P1: Analyze a portfolio."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import math
from util import get_data, plot_data
import datetime as dt

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def assess_portfolio(sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,1,1), \
    syms = ['GOOG','AAPL','GLD','XOM'], \
    allocs=[0.1,0.2,0.3,0.4], \
    sv=1000000, rfr=0.0, sf=252.0, \
    gen_plot=False):

    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later
   

    # Get daily portfolio value
    port_val = prices_SPY / prices_SPY.ix[0] * sv  # add code here to compute daily portfolio values
    port_val2 = prices / prices.ix[0] * allocs * sv
    
    # Get portfolio statistics (note: std_daily_ret = volatility)
    # add code here to compute stats
    vs = port_val2.sum(axis = 1)
    dr = vs/vs.shift(1) - 1
    dr = dr.ix[1:]
    cr = vs.ix[-1] / sv - 1
    adr = dr.mean()
    sddr = dr.std()
    sr = math.sqrt(sf) * (adr - rfr) /sddr



    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        df = pd.concat([vs/sv, port_val/sv], keys=['Portfolio', 'SPY'], axis=1)
        plot_data(df, title="Daily portfolio value and SPY", xlabel="Date", ylabel="Normalized price")

    # Add code here to properly compute end value
    ev = vs[-1]

    return cr, adr, sddr, sr, ev



if __name__ == "__main__":
    # This code WILL NOT be tested by the auto grader
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!
    start_date = dt.datetime(2010,1,1)
    end_date = dt.datetime(2011,1,1)
    symbols = ['GOOG', 'AAPL', 'GLD', 'XOM']
    allocations = [0.2, 0.2, 0.4, 0.2]
    start_val = 1000000  
    risk_free_rate = 0.0
    sample_freq = 252

    # Assess the portfolio
    cr, adr, sddr, sr, ev = assess_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        allocs = allocations,\
        sv = start_val, \
        gen_plot = True)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocations
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr
