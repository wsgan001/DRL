

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from Agent import Agent

import matplotlib.pyplot as plt
import tensorflow as tf
import math
import argparse
import sys
import numpy as np
import os

from AutoEncoder.autoencoder import AutoEncoder


class lmmodel(Agent):

    def __init__(self,sess,FileList):
        super(lmmodel, self).__init__('/home/swy/code/DRL/0607/Info1/Info/data/IF1601.CFE.csv', 10)

        self.inputSize=10  #2features
        self.stepNum=10  
        self.hiddenSize=100 # fully connected outputs
        self.neuronNum=20
 
        self.L=FileList
        self.sess =sess
     
        #-------------dropout/产生动作的模式----------
        self.istrain = True

        self.buildNetwork()

        self.saver = tf.train.Saver(tf.global_variables())
       
       

    #input states sequence, generate the action vector by policy Network
    def choose_action(self, state):  
        """Choose an action."""
        state = np.reshape(state, [-1, self.inputSize])
        context = {}
        context.update({self.stateTrain:state})
        return self.sess.run(self.argAction, feed_dict=context)
       # return self.sess.run(self.curarg, feed_dict=context)

    def enterParameter(self,session,fullyConnected):
        self.weights_dict = fullyConnected[0]
        self.biases_dict = fullyConnected[1]
      #  self.paraDict={self.weights1:self.weights_dict['weights1'], self.weights2: self.weights_dict['weights2'], self.weights3: self.weights_dict['weights3'], self.biases1: self.biases_dict['biases1'],
      #              self.biases2: self.biases_dict['biases2'],self.biases3: self.biases_dict['biases3']}
        session.run(self.update_w1,feed_dict={self.weights1:self.weights_dict['weights1']})      
        session.run(self.update_w2,feed_dict={self.weights2:self.weights_dict['weights2']})   
        session.run(self.update_w3,feed_dict={self.weights3:self.weights_dict['weights3']})   
        session.run(self.update_b1,feed_dict={self.biases1:self.biases_dict['biases1']})   
        session.run(self.update_b2,feed_dict={self.biases2:self.biases_dict['biases2']})   
        session.run(self.update_b3,feed_dict={self.biases3:self.biases_dict['biases3']})       

    # build the policy Network and value Network
    def buildNetwork(self):
        self.stateTrain = tf.placeholder(tf.float32,shape=[None, self.inputSize],name= "stateTrain")
        self.critic_rewards = tf.placeholder(tf.float32,shape=[None],name= "critic_rewards")

        self.new_lr = tf.placeholder(tf.float32,shape=[],name="learning_rate")
        self.lr = tf.Variable(0.01, trainable=False)

        # PolicyNetwork

        with tf.variable_scope("Policy") :

            self.weights1 = tf.placeholder(tf.float32, shape = [self.inputSize, self.hiddenSize], name = "weights1")
            self.biases1 = tf.placeholder(tf.float32, shape = [self.hiddenSize], name = "biases1")
            self.weights2 = tf.placeholder(tf.float32, shape=[self.hiddenSize, self.hiddenSize], name="weights2")
            self.biases2 = tf.placeholder(tf.float32, shape=[self.hiddenSize], name="biases2")
            self.weights3 = tf.placeholder(tf.float32, shape=[self.hiddenSize, self.hiddenSize], name="weights3")
            self.biases3 = tf.placeholder(tf.float32, shape=[self.hiddenSize], name="biases3")
            #变量保存
            self.w1= tf.get_variable( "w1", [self.inputSize, self.hiddenSize], dtype=tf.float32,initializer=tf.truncated_normal_initializer(stddev=1.0/math.sqrt(float(self.hiddenSize))),trainable=True)
            self.b1 = tf.get_variable("b1", [self.hiddenSize], dtype=tf.float32,initializer=tf.zeros_initializer(),trainable=True)
            self.w2= tf.get_variable( "w2", [self.hiddenSize, self.hiddenSize], dtype=tf.float32,initializer=tf.truncated_normal_initializer(stddev=1.0/math.sqrt(float(self.hiddenSize))),trainable=True)
            self.b2 = tf.get_variable("b2", [self.hiddenSize], dtype=tf.float32,initializer=tf.zeros_initializer(),trainable=True)
            self.w3= tf.get_variable( "w3", [self.hiddenSize, self.hiddenSize], dtype=tf.float32,initializer=tf.truncated_normal_initializer(stddev=1.0/math.sqrt(float(self.hiddenSize))),trainable=True)
            self.b3 = tf.get_variable("b3", [self.hiddenSize], dtype=tf.float32,initializer=tf.zeros_initializer(),trainable=True)
            
            self.update_w1 = tf.assign(self.w1,self.weights1)
            self.update_w2 = tf.assign(self.w2,self.weights2)
            self.update_w3 = tf.assign(self.w3,self.weights3)
            self.update_b1 = tf.assign(self.b1,self.biases1)
            self.update_b2 = tf.assign(self.b2,self.biases2)
            self.update_b3 = tf.assign(self.b3,self.biases3)

            activation = tf.nn.relu

            L0 = activation(tf.matmul(self.stateTrain, self.w1)+self.b1)
            L1 = activation(tf.matmul(L0, self.w2)+self.b2)
            L2 = activation(tf.matmul(L1, self.w2)+self.b2)

            L2 = tf.reshape(L2, [1, -1, self.hiddenSize])
            #construct a lstmcell ,the size is neuronNum
            cell = tf.contrib.rnn.BasicRNNCell(self.neuronNum)
            if self.istrain:
                print("dropout")
                cell =tf.contrib.rnn.DropoutWrapper(cell, output_keep_prob=0.5)
            #lstmcell = tf.contrib.rnn.BasicLSTMCell(self.neuronNum, forget_bias=1.0, state_is_tuple=True,activation=tf.nn.relu)
            #cell_drop=tf.contrib.rnn.DropoutWrapper(lstmcell, output_keep_prob=0.5)
            #cell = tf.contrib.rnn.MultiRNNCell([cell_drop for _ in range(2)], state_is_tuple=True)
            print("gogog")

            
            outputnew, statenew = tf.nn.dynamic_rnn(cell, L2, dtype=tf.float32)
            if self.modetype == 0:
                #---------------------------产生连续动作，stepnum长度，取第一个值-----------------------
                outputs = self.outputs = tf.reshape(outputnew,[-1,self.stepNum,self.neuronNum])
                outputs = outputs[:,0,:]
               
            else:
                #---------------------------直接取每个动作的值------------------------------
                outputs = self.outputs = tf.reshape(outputnew,(-1,self.neuronNum))

            
            softmax_w = tf.get_variable( "softmax_w", [self.neuronNum, 3], dtype=tf.float32,initializer=tf.truncated_normal_initializer(stddev=1.0/math.sqrt(float(self.neuronNum))))
            softmax_b = tf.get_variable("softmax_b", [3], dtype=tf.float32)
            logits = tf.matmul(outputs, softmax_w) + softmax_b
            self.probs = tf.nn.softmax(logits, name="action")

            # fetch the maximum probability # fetch the index of the maximum probability
            self.action0 = tf.reduce_max(self.probs, axis=1)
            self.argAction = tf.argmax(self.probs, axis=1)

            #--------------------------continuous action-----------
            #curact = tf.reshape(self.action0,[-1,30])
            #curarg = tf.reshape(self.argAction,[-1,30])
            #--------------------------result-----------------------
            #self.curact = curact[:,29]
            #self.curarg = curarg[:,29]
            #self.policyloss = policyloss = tf.log(self.curact)*self.critic_rewards 
            #self.loss = loss = tf.negative(tf.reduce_mean(policyloss),name="loss")

            #loss,train 
            self.lr_update = tf.assign(self.lr,self.new_lr)
            self.policyloss = policyloss = tf.log(self.action0)*self.critic_rewards 
            self.loss = loss = tf.negative(tf.reduce_mean(policyloss),name="loss")
            tf.summary.scalar('actor_loss',loss)
            #self.actor_train = tf.train.AdamOptimizer(self.lr).minimize(loss)
            tvars = tf.trainable_variables() #得到可以训练的参数
            self.agrads, _ = tf.clip_by_global_norm(tf.gradients(loss, tvars),5)  #防止梯度爆炸
            optimizer = tf.train.AdamOptimizer(self.lr)
            self.actor_train = optimizer.apply_gradients(zip(self.agrads, tvars))
    
    #给learning rate 赋值
    def assign_lr(self,session,lr_value):
        session.run(self.lr_update,feed_dict={self.new_lr:lr_value})

    # 计算折扣因子
    def discount_rewards(self,rewards,discount_rate):
        discounted_rewards = np.empty(len(rewards))
        cumulative_rewards = 0
        for step in reversed(range(len(rewards))):
            cumulative_rewards = rewards[step] + cumulative_rewards*discount_rate
            discounted_rewards[step] = cumulative_rewards
        return discounted_rewards
    # normalize rewards
    def discount_and_normalize_rewards(self,all_rewards,discount_rate):
        all_discounted_rewards = [self.discount_rewards(rewards,discount_rate) for rewards in all_rewards]
        flat_rewards = np.concatenate(all_discounted_rewards)
        reward_mean = flat_rewards.mean()
        reward_std = flat_rewards.std()
        
        if reward_mean == 0 and reward_std == 0:
            return 0
        else:
            return [(discounted_rewards - reward_mean)/reward_std for discounted_rewards in all_discounted_rewards]


    def learn(self):
        
        
        self.merged = tf.summary.merge_all()
        self.writer = tf.summary.FileWriter("/home/swy/code/DRL/0609/tb", self.sess.graph) 
        #2周
        batchsize=2400
        timestep = self.stepNum
        epoch=100
        #-------learning_rate decay -------
        max_epoch=2
        learningrate = 0.1
        v_sharp = []
        sharp = []
        for j in range(epoch):
            total=[] 
            sharp_tmp = []
            sum = 0
            win = 0
            lr_decay = 0.5**max(j+1 - max_epoch,0.0)
            k=0
            self.istrain=True
            self.modetype = 0
            #for i in range(0,len(self.state)-batchsize,240):
            #------------先训练2周数据，用一天数据做验证，验证标准：夏普比率-----------
            for i in range(1):
                k=k+1
                act_sum = [] #记录每一轮游戏的action
                price_sum = [] #记录训练的价格走势
                #index = np.random.randint(0, len(self.state)-batchsize-timestep)
                trajectory = self.get_trajectory(i, batchsize)
                state = trajectory["state"]
                rew =trajectory["reward"]
                price = trajectory["price"]
                price_sum.append(price)
                returns = self.discount_and_normalize_rewards([rew],0.95)

                sharp_tmp.append(np.mean(rew)/np.std(rew))
                total.append(np.sum(rew))
                action = trajectory["action"]
                #print("train")
                #print(np.shape(action))
                #act_sum = action
                act_sum.append(action)
                if returns == 0:
                    print("over")
                    continue
                else:
                    returns = np.reshape(returns,[-1])
                      
                    #统计收益大于0的周数
                    if np.sum(returns)>0:
                        win = win +1
                    sum = sum +1
                   
                    state = np.reshape(state, [-1, self.inputSize])
                   

                    context = {}
                    #context.update(self.paraDict)
                    context.update({self.stateTrain: state})
                    context.update({self.critic_rewards:returns})
                    probs, loss,action0 = self.sess.run([self.probs, self.policyloss,self.argAction],feed_dict=context)
                    #print (probs)
                    #print (loss)
                    summary,actorResults= self.sess.run([self.merged,self.actor_train],feed_dict=context)
                    self.writer.add_summary(summary,i)

                #-----------------------验证集---------------------------------
                print("validation")
                self.istrain=False
                self.modetype = 1
                v_trajectory = self.get_trajectory(i+2400, 240)
                v_rew =v_trajectory["reward"]
                v_action = v_trajectory["action"]
                #print("v_action")
                #print(np.shape(v_action))
                v_sharp.append(np.mean(v_rew)/np.std(v_rew))
                print(np.mean(v_rew)/np.std(v_rew))
                #print(v_action)
               
                # ---------------------------------action --------------------------------
                if j == 0:
                #if k == 44:
                    plt.figure()      
                    act_sum=np.reshape(act_sum,[-1])   
                    x_values = range(len(act_sum))
                    y_values = act_sum
                    plt.plot(x_values, y_values)
                    #plt.savefig("act:"+str(j)+str(k)+'.png')
                # ---------------------------------price --------------------------------
                if j == 0 :
                    plt.figure()   
                    price_sum=np.reshape(price_sum,[-1])   
                    x_values = range(len(price_sum))
                    y_values = price_sum
                    plt.plot(x_values, y_values)
                   # plt.savefig("price:"+str(j)+str(k)+'.png')
                
        # ---------------------------------shape rato --------------------------------
        plt.figure()     
        x_values = range(len(v_sharp))
        y_values = v_sharp
        plt.plot(x_values, y_values)
        plt.savefig("v_sharp:"+str(j)+str(k)+'.png')
        #sharp_tmp=np.reshape(sharp_tmp,[-1])
        #sharp.append(np.mean(sharp_tmp)/np.std(sharp_tmp))
        plt.figure()
        x_values = range(len(sharp_tmp))
        y_values = sharp_tmp
        plt.plot(x_values, y_values)
        #plt.savefig("sharp:"+str(j)+str(k)+'.png')
        self.writer.close()

        # ---------------------------------profit epoch --------------------------------
        #print(win/sum)        
        plt.figure()
        x_values = range(len(total))
        y_values = total
        plt.plot(x_values, y_values)
        #plt.savefig("returns:"+str(j)+'.png')

            

            
        

        


def main():
    os.chdir("/home/swy/code/DRL/0609/Info1/Info/data")
    L=[]
    for files in os.walk("/home/swy/code/DRL/0609/Info1/Info/data"):
        for file in files:
            L.append(file) 

    if tf.gfile.Exists('/home/swy/code/DRL/0609/tb'):
            tf.gfile.DeleteRecursively('/home/swy/code/DRL/0609/tb')
    tf.gfile.MakeDirs('/home/swy/code/DRL/0609/tb')

    sess= tf.InteractiveSession()
    trainable= True
    if trainable:
        out = lmmodel(sess=sess,FileList=L)
        config = {}
        config['hiddenSize'] = [10, 100, 100,100]
        AETrain = AutoEncoder(config=config)
        AETrain.getTrainData(out.getData())
        AETrain.learn()
        out.enterParameter(sess,AETrain.getParameter())
        sess.run(tf.global_variables_initializer())
        out.learn()
        save_path = out.saver.save(sess, '/home/swy/code/DRL/0607/model0609_d1.ckpt')
    else:
        out = lmmodel(sess=sess,FileList=L)
        load_path = out.saver.restore(sess,'/home/swy/code/DRL/0607/model0609_d1.ckpt')
        out.learn()
        #save_path = out.saver.save(sess, '/home/swy/code/DRL/0607/model0605_d3.ckpt')



if __name__ == '__main__':
    main()
    #tf.app.run()














    





    
