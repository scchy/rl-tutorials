#!/usr/bin/env python
# coding=utf-8
'''
@Author: John
@Email: johnjim0816@gmail.com
@Date: 2020-06-12 00:48:57
@LastEditor: John
LastEditTime: 2021-03-30 10:56:54
@Discription: 
@Environment: python 3.7.7
'''
import sys,os
from pathlib import Path
import sys,os
curr_path = os.path.dirname(__file__)
parent_path=os.path.dirname(curr_path) 
sys.path.append(parent_path) # add current terminal path to sys.path

import gym
import torch
import datetime
from DQN.agent import DQN
from common.plot import plot_rewards
from common.utils import save_results

SEQUENCE = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") # obtain current time
SAVED_MODEL_PATH = curr_path+"/saved_model/"+SEQUENCE+'/' # path to save model
if not os.path.exists(curr_path+"/saved_model/"): 
    os.mkdir(curr_path+"/saved_model/")
if not os.path.exists(SAVED_MODEL_PATH): 
    os.mkdir(SAVED_MODEL_PATH)
RESULT_PATH = curr_path+"/results/"+SEQUENCE+'/' # path to save rewards
if not os.path.exists(curr_path+"/results/"): 
    os.mkdir(curr_path+"/results/")
if not os.path.exists(RESULT_PATH): 
    os.mkdir(RESULT_PATH)

class DQNConfig:
    def __init__(self):
        self.algo = "DQN"  # name of algo
        self.gamma = 0.99
        self.epsilon_start = 0.95 # e-greedy策略的初始epsilon
        self.epsilon_end = 0.01
        self.epsilon_decay = 200
        self.lr = 0.01 # 学习率
        self.memory_capacity = 800 # Replay Memory容量
        self.batch_size = 64
        self.train_eps = 300 # 训练的episode数目
        self.train_steps = 200 # 训练每个episode的最大长度
        self.target_update = 2 # target net的更新频率
        self.eval_eps = 20 # 测试的episode数目
        self.eval_steps = 200 # 测试每个episode的最大长度
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # 检测gpu
        self.hidden_dim = 128 # 神经网络隐藏层维度
 
def train(cfg,env,agent):
    print('Start to train !')
    rewards = []
    ma_rewards = [] # moveing average reward
    for i_episode in range(cfg.train_eps):
        state = env.reset() 
        ep_reward = 0
        while True:
            action = agent.choose_action(state) 
            next_state, reward, done, _ = env.step(action) 
            ep_reward += reward
            agent.memory.push(state, action, reward, next_state, done) 
            state = next_state 
            agent.update() 
            if done:
                break
        if i_episode % cfg.target_update == 0:
            agent.target_net.load_state_dict(agent.policy_net.state_dict())
        print('Episode:{}/{}, Reward:{}'.format(i_episode+1,cfg.train_eps,ep_reward))
        rewards.append(ep_reward)
        # 计算滑动窗口的reward
        if ma_rewards:
            ma_rewards.append(
                0.9*ma_rewards[-1]+0.1*ep_reward)
        else:
            ma_rewards.append(ep_reward)   
    print('Complete training！')
    return rewards,ma_rewards

if __name__ == "__main__":
    cfg = DQNConfig()
    env = gym.make('CartPole-v0')
    env.seed(1)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    agent = DQN(state_dim,action_dim,cfg)
    rewards,ma_rewards = train(cfg,env,agent)
    agent.save(path=SAVED_MODEL_PATH)
    save_results(rewards,ma_rewards,tag='train',path=RESULT_PATH)
    plot_rewards(rewards,ma_rewards,tag="train",algo = cfg.algo,path=RESULT_PATH)
