# SnakeRL — Phase 2

Phase 2 takes the classic snake game from Phase 1 and turns it into a full reinforcement learning project. The snake learns to play itself using a Deep Q-Network, and the whole game gets a massive visual and gameplay upgrade.


## What's New in Phase 2

### AI That Learns to Play
- **DQN Agent** — the snake trains itself using Deep Q-Learning with experience replay
- **11-dimensional state** — the agent sees danger directions, its own heading, and where the food is
- **Epsilon-greedy exploration** — starts random, gradually shifts to exploiting what it's learned
- **Live training plots** — watch the score curve climb in real time with matplotlib
- **GPU support** — automatically uses CUDA if available

### Way More Gameplay
- **Power-ups** — speed boost, shield (absorbs one hit), and double points randomly spawn on the field
- **Combo system** — eat food quickly in succession to stack combo multipliers
- **Obstacles** — rocks start appearing at higher levels, making the snake's life harder
- **Magnet mode** — press `W` to pull food toward you (unlocks at level 3, has a cooldown)
- **Leveling** — every 5 points bumps up the level, which increases speed and spawns obstacles
- **Pause menu** — press `P` or `Esc` to pause, resume, or quit to menu

### Neon Visual Overhaul
- Dark background with animated grid and floating particles
- Gradient snake body with glowing head and trailing particles
- Pulsing food orb with rotating ring particles
- Spinning diamond power-up icons with glow effects
- Screen flash and particle bursts on eating and dying
- CRT scanline overlay for that retro-futuristic look
- Animated HUD with score counter, combo indicator, and effect pills

### Modular Codebase
Phase 1 was a single script. Phase 2 is properly structured:

```
Phase2/
├── play.py              # launch the game
├── train.py             # train the AI agent
├── requirements.txt
├── game/
│   ├── settings.py      # all constants in one place
│   ├── snake_game.py    # human-playable game loop
│   ├── snake_env.py     # gym-style RL environment
│   └── renderer.py      # neon renderer with particles
├── rl/
│   ├── agent.py         # DQN agent with replay buffer
│   ├── model.py         # neural network (3-layer FC)
│   └── utils.py         # training plot helper
└── models/
    └── snake_dqn.pth    # saved model weights
```


## How To Play

### Install Dependencies
```bash
cd Phase2
pip install -r requirements.txt
```

### Play the Game
```bash
python play.py
```


### Train the Agent
```bash
python train.py --episodes 1000
```


## How the RL Works

The agent uses a standard DQN setup:

1. **State** — 11 binary/boolean features: 3 danger flags (straight, right, left), 4 direction bits, 4 food-relative flags
2. **Actions** — 3 choices: go straight, turn right, turn left
3. **Rewards** — +10 for eating, -10 for dying, ±1 for moving toward/away from food
4. **Network** — simple feedforward: 11 → 256 → 128 → 3
5. **Training** — online updates after each step + batch replay from a 100k experience buffer at end of each episode

After ~1000 episodes, the agent consistently scores 20+ and avoids basic traps. 
More episodes = better play.
