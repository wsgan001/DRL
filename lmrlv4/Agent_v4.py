import numpy as np

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
      
        #计算价差zt
        self.diff = []
        for i in range(len(self.dataBase)):
            self.dataBase[i] = float(self.dataBase[i])
        for i in range(1, len(self.dataBase)):
             self.diff.append(self.dataBase[i] - self.dataBase[i-1])


        #将连续m个的特征放在一个状态中
        for i in range(0,len(self.diff)-m+1):
            #self.state.append(self.dataBase[i:i+m]+self.diff[i:i+m])
            self.state.append(self.diff[i:i+m])



    def choose_action(self,state):
        pass
       # return np.random.randint(-1,2)

    def get_state(self,i):
        #index = np.random.randint(0, len(self.state)-self.batchSize+1)
        index = i*100
        state = self.state[index:index+self.batchSize]
        return state

    def get_reward(self,state,action):
        rewards=[float(0)]
        #print(np.shape(state))
        #print(np.shape(action))
        #print(len(action))
        state=np.reshape(state,[-1,10])
        action=np.reshape(action,[-1])
        action = action - 1
        #print(np.shape(state))
        print(np.shape(action))
        for i in range(1,len(action)):
            reward=action[i-1]*state[i][-1]-1*abs(action[i]-action[i-1])
            rewards.append(reward)
        return rewards


    def get_trajectory(self,i):
      
        index = i*100
        state = self.state[index:index+self.batchSize]
        action = self.choose_action(state)
        #print(action)
        #print(np.shape(action))
        #print('----')
        action = action -1
        #print(action)
        rewards = [float(0)]
        for i in range(1, self.batchSize):
            rew = action[i-1] * state[i][-1] - 1 * abs(action[i]-action[i-1])
            #print(rew)
            rewards.append(rew)
        #print(rewards)

        return {"reward":rewards,
                "state": state,
                "action": action
                }

    def get_trajectories(self):
        #
        index=10
        trajectories = []
        i=0
        #while i < self.trajecNum and index<=len(self.state)-self.batchSize+1:
        while i < self.trajecNum:
            i += 1
            trajectory = self.get_trajectory()
            index +=1
            trajectories.append(trajectory)
        return trajectories
