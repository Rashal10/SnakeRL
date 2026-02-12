import torch
import torch.nn as nn
import os

from game.settings import RL_STATE_SIZE, RL_ACTION_SIZE, RL_HIDDEN_1, RL_HIDDEN_2


class DQN(nn.Module):

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(RL_STATE_SIZE, RL_HIDDEN_1),
            nn.ReLU(),
            nn.Linear(RL_HIDDEN_1, RL_HIDDEN_2),
            nn.ReLU(),
            nn.Linear(RL_HIDDEN_2, RL_ACTION_SIZE),
        )

    def forward(self, x):
        return self.net(x)

    def save(self, path="models/snake_dqn.pth"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.state_dict(), path)

    def load(self, path="models/snake_dqn.pth"):
        if os.path.exists(path):
            self.load_state_dict(torch.load(path, weights_only=True))
