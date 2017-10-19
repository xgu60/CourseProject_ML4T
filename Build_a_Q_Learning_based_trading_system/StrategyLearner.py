import numpy as np
import pandas as pd
import datetime as dt
import QLearner as ql
import random as rand
import util as ul

class StrategyLearner(object):

    def __init__(self, verbose=False):
        self.verbose = verbose
        #initialize the Qlearner
        self.ql = ql.QLearner(num_states=288, num_actions = 3, alpha = 0.2, gamma = 0.9, rar = 0.99, radr = 0.99, dyna = 200, verbose = False)

    def addEvidence(self, symbol = "IBM", sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), sv = 10000):
        #calculate the bollinger band
        df = self.bollinger(sd, ed, [symbol])
        
        #set timeStamp and counts
        timeStamp = dt.datetime.now()
        counts = 0

        for j in range(100):
            #initialize dataframe 
            df['trade'] = np.zeros(len(df.index))
            df['hold'] = np.zeros(len(df.index))
            df['cash'] = np.zeros(len(df.index))
            df['cash'][0] = sv
            df['portval'] = np.zeros(len(df.index))
            df['portval'][0] = sv
            
            #initial state s
            s = self.states(df.ix[0][symbol], df.ix[0]['upper'], df.ix[0]['sma'], df.ix[0]['lower'], df.ix[1][symbol], df.ix[1]['upper'], df.ix[1]['sma'], df.ix[1]['lower'], df.ix[0]['hold'])  
            
            #initial action          
            action = self.ql.querysetstate(s)
            
            #update dataframe based on initial action
            operation = [0, 100, -100]
            df['trade'][1] = operation[action]
            df['hold'][1] = df.ix[1]['trade'] + df.ix[0]['hold']
            df['cash'][1] = df.ix[0]['cash'] - df.ix[1][symbol] * df.ix[1]['trade']
            df['portval'][1] = df.ix[1]['cash'] + df.ix[1][symbol] * df.ix[1]['hold']
            
            #setup penalty for violation of the holding law
            #initial penalty equal zero            
            penalty = 0
            
            #iteration starts from day3
            for i in range(2, len(df.index)):
                #calculate the s_prime
                s_prime = self.states(df.ix[i-1][symbol], df.ix[i-1]['upper'], df.ix[i-1]['sma'], df.ix[i-1]['lower'], df.ix[i][symbol], df.ix[i]['upper'], df.ix[i]['sma'], df.ix[i]['lower'], df.ix[i-1]['hold'])
                
                #update penalty value
                if df['hold'][i-1] > 100 or df['hold'][i-1] < -100:
                    penalty = 10000
                else:
                    penalty = 0
                
                #calculate r
                r = df.ix[i-1]['portval'] - df.ix[i-2]['portval'] - penalty
                
                #update Qtable, and give new action
                action = self.ql.query(s_prime, r)
                
                #update dataframe
            	df.ix[i]['trade'] = operation[action]
                df['hold'][i] = df.ix[i]['trade'] + df.ix[i-1]['hold']
                df['cash'][i] = df.ix[i-1]['cash'] - df.ix[i][symbol] * df.ix[i]['trade']
                df['portval'][i] = df.ix[i]['cash'] + df.ix[i][symbol] * df.ix[i]['hold']
            
            #break the loop, if it costs more than 28 seconds
            if dt.datetime.now() - timeStamp > dt.timedelta(seconds=28):
                break
            
            #stop updating if it converges, showing good return repeatly
            if df['portval'][-1] > 2.0 * sv:
                counts += 1
                if counts > 10:
                    break
            else:   
                count = 0

           


    def testPolicy(self, symbol = "IBM", sd=dt.datetime(2009,1,1), ed=dt.datetime(2010,1,1), sv = 10000): 
        df = self.bollinger(sd, ed, [symbol])
                
        df['trade'] = np.zeros(len(df.index))
        df['hold'] = np.zeros(len(df.index))
        df['cash'] = np.zeros(len(df.index))
        df['cash'][0] = sv
        df['portval'] = np.zeros(len(df.index))
        df['portval'][0] = sv
        operation = [0, 100, -100]

        for i in range(1, len(df.index)):
            s = self.states(df.ix[i-1][symbol], df.ix[i-1]['upper'], df.ix[i-1]['sma'], df.ix[i-1]['lower'], df.ix[i][symbol], df.ix[i]['upper'], df.ix[i]['sma'], df.ix[i]['lower'], df.ix[i-1]['hold'])       
            action = self.ql.querysetstate(s)
            
            #to make sure operations not violate holding law
            temp = operation[action] + df.ix[i-1]['hold']
            if temp > 100 or temp < -100:
                df.ix[i]['trade'] = operation[0]
            else:
                df.ix[i]['trade'] = operation[action]
            
            df['hold'][i] = df.ix[i]['trade'] + df.ix[i-1]['hold']            
            df['cash'][i] = df.ix[i-1]['cash'] - df.ix[i][symbol] * df.ix[i]['trade']
            df['portval'][i] = df.ix[i]['cash'] + df.ix[i][symbol] * df.ix[i]['hold']
            
        #make a dataframe structure    
        trades = pd.DataFrame(df['trade'])
        trades.columns = [symbol]
        
        #print '--benchmark--QLearner--'    
        #print sv-df[symbol][0]*100+df[symbol][-1]*100, df['portval'][-1]        

        return trades

           
    # calculate bollinger bands and SMA of stock
    def bollinger(self, sd = dt.datetime(2007,12,31), ed = dt.datetime(2009,12,31), \
    syms = ['IBM']):

        # Read in adjusted closing prices for given symbols, date range
        dates = pd.date_range(sd, ed)
        prices_all = ul.get_data(syms, dates)  
        prices = prices_all[syms]  # only portfolio symbols
     
        # Calculate rollinger band of IBM
        ave = pd.rolling_mean(prices, window = 20)
        std = pd.rolling_std(prices, window = 20)
        prices['sma'] = ave
        prices['upper'] = ave + 2 * std
        prices['lower'] = ave - 2 * std
        prices = prices.fillna(value=0)
     
        return prices

    #calculate states
    def states(self, day1, day1_up, day1_sma, day1_low, day2, day2_up, day2_sma, day2_low, hold):
        #day1 close comapred with bollinger bands and sma
        if day1 > day1_up:
            a = 0
        elif day1 >= (day1_up + day1_sma) / 2:
            a = 1
        elif day1 >= day1_sma:
            a = 2
        elif day1 >= (day1_low + day1_sma) / 2:
            a = 3
        elif day1 >= day1_low:
            a = 4
        else:
            a = 5
        #day2 close comapred with bollinger bands and sma
        if day2 > day2_up:
            b = 0
        elif day2 >= (day2_up + day2_sma) / 2:
            b = 1
        elif day2 >= day2_sma:
            b = 2
        elif day2 >= (day2_low + day2_sma) / 2:
            b = 3
        elif day2 >= day2_low:
            b = 4
        else:
            b = 5
        #holding states
        if hold == 0:
            c = 0
        elif hold == 100:
            c = 1
        elif hold == -100:
            c = 2
        else:
            c = 3
        #stock close increase  
        if day2 -day1 > 0:
            d = 0
        else:
            d = 1

        return a * 48 + b * 8 + c * 2 + d

def test():
    
    for i in range (10):
        a = dt.datetime.now()
        learner = StrategyLearner(verbose = False) # constructor
    	learner.addEvidence(symbol = "IBM", sd=dt.datetime(2007,12,31), ed=dt.datetime(2009,12,31), sv = 10000) # training step
        b = dt.datetime.now()
        learner.testPolicy(symbol = "IBM", sd=dt.datetime(2007,12,31), ed=dt.datetime(2009,12,31), sv = 10000) # testing step
        c = dt.datetime.now()
        print '--trainingTime--testingTime--'
        print b-a, c-b
        print ''
    

#test()



