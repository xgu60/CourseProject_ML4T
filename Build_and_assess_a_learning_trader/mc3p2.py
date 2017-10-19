import csv
import pandas as pd
import numpy as np
import datetime as dt
import KNNLearner as knn
import LinRegLearner as lrl
from util import get_data, plot_data
from marketsim import compute_portvals, analysis
import matplotlib.pyplot as plt

# use stock price to generate two numpy arraies as trainX, trainY
def getData(sd = dt.datetime(2007,12,31), ed = dt.datetime(2009,12,31),  symb='IBM'):

    dates = pd.date_range(sd, ed)
    price = get_data([symb], dates)
    price = price.dropna()
    
    #calculate rollinger band
    ave = pd.rolling_mean(price[symb], window=20)
    std = pd.rolling_std(price[symb], window=20)
    price['bb'] = (price[symb] - ave) / (2 * std)

    #calculate rollinger band of SPY
    #ave2 = pd.rolling_mean(price['SPY'], window=20)
    #std2 = pd.rolling_std(price['SPY'], window=20)
    #price['SPY_bb'] = (price['SPY'] - ave2) / (2 * std2)

     
    #calculate momentum
    N = 10
    price['mom'] = (price[symb] / price[symb].shift(N) - 1) * 20

    #calculate volatility
    dr = price[symb] / price[symb].shift(1) - 1
    price['vola'] = (pd.rolling_std(dr, window=20) ) * 100

    #calculate future return
    price['fr'] = price[symb].shift(-5) / price[symb] - 1

    price = price.dropna()
    return price, price.as_matrix(columns=['bb', 'vola', 'mom']), price['fr'].as_matrix()

# use predicted future 5 days price to generate orders in orders.csv
def operations(dataframe,  symb='IBM'):
    
    out = csv.writer(open("orders.csv", "w"), delimiter=',',quoting=csv.QUOTE_ALL)
    out.writerow(['Date', 'Symbol', 'Order', 'Shares'])
      
    longStock = False
    shortStock = False
    tempPrice = 0.0
    days = 0
    lenter = []
    senter = []
    exit = []

    for i in range(len(dataframe.index)):
        if longStock:
            days += 1
            if days >= 5 or dataframe[symb][i] >= tempPrice * 1.05:
                longStock = False
                out.writerow([dataframe.index[i].strftime("%Y-%m-%d"),symb, 'SELL', '100'])	
                exit.append(dataframe.index[i])
            else:
                continue

        elif shortStock:
            days += 1
            if days >= 5 or dataframe[symb][i] <= tempPrice * 0.98:
                shortStock = False
                out.writerow([dataframe.index[i].strftime("%Y-%m-%d"),symb, 'BUY', '100'])
                exit.append(dataframe.index[i])
            else:
                continue

        elif dataframe['pred'][i] < - 0.01:
            days = 0
            shortStock = True
            tempPrice = dataframe[symb][i]
            out.writerow([dataframe.index[i].strftime("%Y-%m-%d"),symb, 'SELL', '100'])
            senter.append(dataframe.index[i])

        elif dataframe['pred'][i] > 0.01:
            days = 0
            longStock = True
            tempPrice = dataframe[symb][i]
            out.writerow([dataframe.index[i].strftime("%Y-%m-%d"),symb, 'BUY', '100'])
            lenter.append(dataframe.index[i])

    return lenter, senter, exit

#plot different figures
def plot_corr(real, pred):
    plt.figure()
    plt.scatter(real,  pred, color='blue')
    plt.title('correlation')
    plt.xlabel('real')
    plt.ylabel('pred')
    plt.show()

def plot_compare(current, train, pred):
    plt.figure()
    plt.plot(current,  color='black', label='current')
    plt.plot(train,  color='blue', label='train')
    plt.plot(pred,  color='red', label='pred')
    plt.title('trainY vs predY vs CurrentPrice')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend(loc = 2)
    plt.show()

def plot_trade(df, symb, longEntry, shortEntry, exit):
    plt.plot(df, color = 'blue', label = symb)
    plt.legend(loc = 2)
    for date in longEntry:
        plt.axvline(x = date, color = 'green')
    for date in shortEntry:
        plt.axvline(x = date, color = 'red')
    for date in exit:
        plt.axvline(x = date, color = 'black')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend(loc = 2)
    plt.show()

def plot_bt(portvals, symb, SPY):
    plt.plot(portvals, color = 'blue', label = symb)
    plt.plot(SPY, color = 'red', label = 'SPY')
    plt.xlabel('Date')
    plt.ylabel('Potofolio value')
    plt.legend(loc = 2)
    plt.show()


def test(learner=knn.KNNLearner(3), symb='IBM', train_sd=dt.datetime(2007,12,31), train_ed=dt.datetime(2009,12,31), test_sd=dt.datetime(2007,12,31), test_ed=dt.datetime(2009,12,31)):

    #create a learner
    learner = learner

    #generate training dataset
    df, trainX, trainY = getData(train_sd, train_ed, symb)
    #add evidence
    learner.addEvidence(trainX, trainY)
    #generate testing dataset
    df2, testX, testY = getData(test_sd, test_ed, symb)
    #use learner to predict value
    predY = learner.query(testX)
    
    #plot correlations between test and predict data, and calculate their correlation
    plot_corr(testY, predY)
    c = np.corrcoef(predY, y=testY)
    print "corr: ", c[0,1]

    #generate plot for current price, train price and predict price
    df2['pred'] = predY
    df2['fv'] = df2[symb] * (1 + df2['fr'])
    df2['pv'] = df2[symb] * (1 + df2['pred']) 
    plot_compare(df2[symb], df2['fv'], df2['pv'])

    #use predict data to execute orders and plot long, short, exit as vertical lines
    le, se, s = operations(df2,  symb)
    plot_trade(df2[symb], symb, le, se, s) 

    #computer portvals plot backtest results
    portvals = compute_portvals("orders.csv", start_val=10000)
    norm_SPY = df2['SPY']/df2['SPY'][0] * 10000
    plot_bt(portvals, symb, norm_SPY)
 
    #analysis of portfolio
    cr, adr, sddr, sr = analysis(portvals)
    print cr, adr, sddr, sr, portvals[-1]

#choose learner, stock symbol, training start date and end date, plus test strat date and end date
#in sample test, use same start date and end date 
#out of sample test, use different start date and end date
test(learner=knn.KNNLearner(3), symb='IBM', train_sd=dt.datetime(2007,12,31), train_ed=dt.datetime(2009,12,31), test_sd=dt.datetime(2007,12,31), test_ed=dt.datetime(2009,12,31))



