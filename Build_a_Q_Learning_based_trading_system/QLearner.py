"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand

class QLearner(object):

    def __init__(self, \
        num_states=100, \
        num_actions = 4, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):
        
        self.q = np.random.random((num_states, num_actions)) * 2 - 1
        self.list = []
        self.verbose = verbose
        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.s = 0
        self.a = 0

    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        self.s = s
        #action = rand.randint(0, self.num_actions-1)
        action = np.argmax(self.q[s]) 
        self.a = action
        if self.verbose: print "s =", s,"a =",action
        return action

    def query(self,s_prime,r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        
              
        self.list.append((self.s, self.a, s_prime, r))
        for i in range(self.dyna):
            pair = rand.choice(self.list)
              
            self.q[pair[0]][pair[1]] = (1 - self.alpha) * self.q[pair[0]][pair[1]] + self.alpha * (pair[3] + self.gamma * self.q[pair[2]][np.argmax(self.q[pair[2]]) ]) 

        
        rd = rand.random()
        if rd < self.rar:
            action = rand.randint(0, self.num_actions-1)
        else:
            action = np.argmax(self.q[s_prime]) 
       
        self.q[self.s][self.a] = (1 - self.alpha) * self.q[self.s][self.a] + self.alpha * (r + self.gamma * self.q[s_prime][action]) 
        self.a = action               
        self.s = s_prime
        self.rar *= self.radr
                    
        if self.verbose: print "s =", s_prime,"a =",action,"r =",r
        return action
        

if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
