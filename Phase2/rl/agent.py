import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

from rl.model import DQN
from game.settings import (
    RL_LEARNING_RATE, RL_GAMMA,
    RL_EPSILON_START, RL_EPSILON_MIN, RL_EPSILON_DECAY,
    RL_BATCH_SIZE, RL_MEMORY_SIZE, RL_ACTION_SIZE,
)


class DQNAgent:

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = DQN().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=RL_LEARNING_RATE)
        self.criterion = nn.MSELoss()

        self.memory = deque(maxlen=RL_MEMORY_SIZE)
        self.epsilon = RL_EPSILON_START
        self.gamma = RL_GAMMA
        self.n_games = 0


    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, RL_ACTION_SIZE - 1)

        state_t = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            q_values = self.model(state_t)
        return int(torch.argmax(q_values).item())


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))


    def train_short_memory(self, state, action, reward, next_state, done):
        self._train_step([(state, action, reward, next_state, done)])

    def train_long_memory(self):
        if len(self.memory) < RL_BATCH_SIZE:
            batch = list(self.memory)
        else:
            batch = random.sample(self.memory, RL_BATCH_SIZE)
        self._train_step(batch)

    def _train_step(self, batch):
        states, actions, rewards, next_states, dones = zip(*batch)

        states_t = torch.tensor(np.array(states), dtype=torch.float32, device=self.device)
        next_states_t = torch.tensor(np.array(next_states), dtype=torch.float32, device=self.device)
        actions_t = torch.tensor(actions, dtype=torch.long, device=self.device)
        rewards_t = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        dones_t = torch.tensor(dones, dtype=torch.bool, device=self.device)

        # current Q
        q_pred = self.model(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)

        # target Q
        with torch.no_grad():
            q_next = self.model(next_states_t).max(dim=1)[0]
            q_next[dones_t] = 0.0
        q_target = rewards_t + self.gamma * q_next

        loss = self.criterion(q_pred, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    #Epsilon Decay

    def decay_epsilon(self):
        self.epsilon = max(RL_EPSILON_MIN, self.epsilon * RL_EPSILON_DECAY)


    def save(self, path="models/snake_dqn.pth"):
        self.model.save(path)

    def load(self, path="models/snake_dqn.pth"):
        self.model.load(path)
        self.model.to(self.device)
