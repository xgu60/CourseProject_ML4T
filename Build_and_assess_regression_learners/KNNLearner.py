import numpy as np
import math


class KNNLearner(object):

    def __init__(self, k=3, verbose=False):
        self.k = k
        self.v = verbose

    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        # build and save the model
        
        self.x = dataX
        self.y = dataY
        
        
        
    def query(self,points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
            
        predY = []
        
        for point in points: 
            diff = (self.x[:, 0] - point[0])**2 + (self.x[:, 1] - point[1])**2
            data = np.column_stack((self.y, diff))
            data = data[data[:, 1].argsort()]
            predY.append(data[:self.k, 0].mean())
             
        if self.v:
            print predY
        return np.array(predY)

if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
