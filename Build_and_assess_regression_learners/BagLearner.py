import numpy as np
import pandas as pd
import LinRegLearner as lrl
import KNNLearner as knn

class BagLearner(object):

    def __init__(self, learner = knn.KNNLearner, kwargs = {"k": 3}, bags = 20, boost = False, verbose = False):
        self.learners = []
        self.boost = boost
        self.verbose = verbose
        kwargs = kwargs
        for i in range(0, bags):
            self.learners.append(learner(**kwargs))
       
        
        
       

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        # build and save the model
        
        
        for i in range(len(self.learners)):
            index = np.random.randint(0, dataX.shape[0], dataX.shape[0])
            self.learners[i].addEvidence(dataX[index], dataY[index])
            
        
        
        
    def query(self,points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        df = pd.DataFrame()
        for i in range(len(self.learners)):
            df[str(i)] = self.learners[i].query(points).tolist()
        return df.mean(axis=1)
        
            


if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
