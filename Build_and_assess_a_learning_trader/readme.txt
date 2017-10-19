How to run the code to generate all plots presented in my report.

1) download util.py, marketsim.py, KNNLearner.py, mc3p2.py in the same fold.

2) open mc3p2.py, fill stock symbol, traindata start data, end date, testdata start date and end date as parameters of function test().
 
example: in-sample IBM

test(learner=knn.KNNLearner(3), symb='IBM', train_sd=dt.datetime(2007,12,31), train_ed=dt.datetime(2009,12,31), test_sd=dt.datetime(2007,12,31), test_ed=dt.datetime(2009,12,31))

example: out-of-sample IBM

test(learner=knn.KNNLearner(3), symb='IBM', train_sd=dt.datetime(2007,12,31), train_ed=dt.datetime(2009,12,31), test_sd=dt.datetime(2009,12,31), test_ed=dt.datetime(2011,12,31))
