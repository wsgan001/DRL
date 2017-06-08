import numpy as np
import matplotlib.pyplot as plt
"""
 m:ft,feature
 batchSize: a trajectory
 batchLength: trajectories
"""

class Agent(object):

    def __init__(self, fileName, timeStep):
        # -----------------------------------data initial--------------------------------
        self.action_space = [-1, 0, 1]
        self.timeStep = timeStep
        self.f_matrix = np.loadtxt(open(fileName,'rb'), delimiter=',', skiprows=5)
        #价差(涨跌)，价格
        self.diff = self.f_matrix[:, 7]
        self.close = self.f_matrix[:,4]

        mode = 2
        if mode == 1:
            # ---------------------------------data transform1--------------------------------
            self.state=[]
            for i in range(len(self.diff)):
                state = self.f_matrix[i,1:11]
                self.state.append(state)

            self.data = []  #每10（timestep）分钟进行一次决策‘
            self.price =[] #环境价格
            interval = 1
            for i in range(0,len(self.f_matrix)-timeStep,interval):
                rowTmp = []
                for j in range(timeStep):
                    rowTmp.append(self.state[i+j])
                self.data.append(rowTmp)  #认为未来对于现在影响，训练数据，非在线学习过程??????
                self.price.append(self.close[i+timeStep-1]) #待定义
            #self.state2D = np.reshape(self.data, [-1, 7]) # 包含重复状态
            self.state2D = self.state #不包含重复状态
        elif mode == 2:

            self.state=[]
            for i in range(len(self.diff)):
                state = self.f_matrix[i,1:11]
                self.state.append(state)
            self.data = self.state
            self.price = self.close
            self.state2D = self.state
        else:
            # ---------------------------------data transform2-------------------------------- 
            self.state=[] #每个状态由前50价差组成
            for i in range(len(self.diff)-50):
                state = self.diff[i:i+50]
                self.state.append(state)
            self.data = []
            self.price = []
            for i in range(len(self.state)-timeStep): #每个状态受前timestep个状态影响
                rowTmp = []
                for j in range(timeStep):
                    rowTmp.append(self.state[i+j])
                self.data.append(rowTmp)
                self.price.append(self.close[50+i+timeStep-1])
            self.state2D = self.state


    def getData(self):
        return self.state2D

    def get_trajectory(self, index, batchSize):
        # ---------------state Get--------------------
        batch = self.data[index:index+batchSize]

        # ---------------action Get-------------------
        action = self.choose_action(batch)-1

        #------------add to the length of batch------------------------
        action0 = []
        for i in range(len(action)):
            for j in range(self.timeStep):
                action0.append(action[i])

        # ---------------reward Get-------------------
        rewards = []
        #diff = self.diff[index+self.timeStep:index+self.timeStep+batchSize] #不包含最后一个
        price = self.price[index:index+batchSize]
        
        for i in range(len(action0)):
            if i==0:
                rew = - 1* abs(action0[i])
            else:
                #rew = action[i-1] * diff[i] - 1* abs(action[i]-action[i-1])
                rew = action0[i-1] *(price[i]-price[i-1])  - 1* abs(action0[i]-action0[i-1])
            rewards.append(rew)
        
        rewards = np.reshape(rewards,[-1,self.timeStep])
        rews = rewards[:,-1]
    
        return {"reward":rews,
                "state": batch,
                "action": action0,
                "price" : price
                }

    def choose_action(self, state):
        pass



  