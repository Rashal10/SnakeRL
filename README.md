# SnakeRL

A snake game that evolves from a classic Pygame project into a reinforcement learning playground. Built in two phases — first a playable game, then an AI that learns to play it.

---

## Phases

### [Phase 1 — Classic Snake](Phase1/)
The starting point. A simple, fun snake game built with Pygame:
- Arrow key controls with wrap-around walls
- Custom apple sprite for food
- Score tracking, levels, and high score persistence
- Snake with tongue animation and checkered background

Good for learning Pygame basics. One file, no dependencies beyond `pygame`.

### [Phase 2 — RL + Visual Overhaul](Phase2/)
Everything from Phase 1, rebuilt from scratch with a modular architecture and a DQN agent that learns to play:

**AI & RL**
- Deep Q-Network with experience replay and epsilon-greedy exploration
- 11-dim state vector → 256 → 128 → 3-action output
- GPU-accelerated training with live score plotting
- Watch mode — load a trained model and see it play

**New Gameplay**
- Power-ups (speed boost, shield, double points)
- Combo multiplier for eating food in quick succession
- Obstacles that spawn at higher levels
- Magnet mode — pull food toward the snake (press `W`, unlocks at level 3)
- Pause menu with resume/quit options

**Visuals**
- Neon dark theme with animated grid and floating particles
- Gradient snake body with glowing head and trails
- Pulsing food orb with orbiting particles
- Screen flash, death particles, and CRT scanline overlay
- Animated score HUD with combo and power-up indicators

---

## Quick Start

### Phase 1
```bash
cd Phase1
pip install pygame
python Snake.py
```

### Phase 2
```bash
cd Phase2
pip install -r requirements.txt

python play.py

# train the AI
python train.py --episodes 1000

python train.py --episodes 1000 --render
```


## Project Structure

```
SnakeRL/
├── README.md
├── Phase1/
│   ├── Snake.py
│   ├── apple.png
│   └── README.md.txt
└── Phase2/
    ├── play.py
    ├── train.py
    ├── requirements.txt
    ├── game/
    │   ├── settings.py
    │   ├── snake_game.py
    │   ├── snake_env.py
    │   └── renderer.py
    ├── rl/
    │   ├── agent.py
    │   ├── model.py
    │   └── utils.py
    └── models/
        └── snake_dqn.pth
```


## Tech Stack

| Component      | Tech                         |
|----------------|------------------------------|
| Game engine    | Pygame                       |
| RL framework   | PyTorch                      |
| State/rewards  | Custom gym-style environment |
| Visualization  | Matplotlib (training plots)  |
| Model          | 3-layer fully connected DQN  |

