import numpy as np
import tensorflow as tf

"""
 m:ft,feature
 batchSize: a trajectory
 batchLength: trajectories
"""

class Agent2(object):

    def __init__(self, fileName, m, batchSize, trajecNum):
        self.action_space = [-1, 0, 1]
        self.m = m
        self.batchSize = batchSize
        self.trajecNum = trajecNum
        self.state = []

        f = open(fileName, 'r')

        self.dataBase = f.readline()
        self.dataBase = self.dataBase.split(',')
        self.dataBase.pop()

        for i in range(len(self.dataBase)):
            self.dataBase[i] = float(self.dataBase[i])
        for i in range(1, len(self.dataBase)):
            self.dataBase[i] = self.dataBase[i] - self.dataBase[i-1]

        for i in range(self.m-1, len(self.dataBase)):
            state_tmp = self.dataBase[i-m+1:i+1] if i >= self.m-1 else self.dataBase[0:i]
            self.state.append(state_tmp)

        self.state = self.state[m-1:]



    def choose_action(self,state):
        pass
       # return np.random.randint(-1,2)




    def get_trajectory(self,index):
        
        state = self.state[index:index+self.batchSize]
        action0=self.choose_action([state])
        action = action0-1
        rewards = [float(0)]
        for i in range(1, self.batchSize):
            rew = action[i-1] * state[i][-1] - 1 * abs(action[i]-action[i-1])
            #print(rew)
            rewards.append(rew)
        print(rewards)

        return {"reward":rewards,
                "state": state,
                "action": action
                }

    def get_trajectories(self):

        trajectories = []
        #index = np.random.randint(0, len(self.state)-self.batchSize+1)
        index=0
        i=0
        while i < self.trajecNum and index<len(self.state)-self.batchSize+1:
            i += 1
            trajectory = self.get_trajectory(index)
            index +=1
            trajectories.append(trajectory)
        return trajectories
