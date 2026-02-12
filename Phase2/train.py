"""Train the DQN agent to play Snake."""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.snake_env import SnakeEnv
from rl.agent import DQNAgent
from rl.utils import plot_training


def train(episodes=500, render=False, plot=True):
    env = SnakeEnv()
    agent = DQNAgent()

    scores = []
    mean_scores = []
    total_score = 0
    record = 0
    model_path = "models/snake_dqn.pth"

    if os.path.exists(model_path):
        agent.load(model_path)
        print(f"  Resumed from {model_path}")

    print(f"  Training for {episodes} episodes...")
    print(f"  Device: {agent.device}")
    print("-" * 50)

    renderer = None
    if render:
        from game.renderer import Renderer
        renderer = Renderer()

    for episode in range(1, episodes + 1):
        state = env.reset()
        done = False

        while not done:
            action = agent.get_action(state)
            next_state, reward, done, info = env.step(action)
            agent.train_short_memory(state, action, reward, next_state, done)
            agent.remember(state, action, reward, next_state, done)

            state = next_state

            if renderer:
                import pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        renderer.quit()
                        return

                renderer.draw_background()
                renderer.draw_obstacles(env.get_obstacle_pixels())
                renderer.draw_food(env.get_food_pixel())
                renderer.draw_snake(env.get_snake_pixels(), env.direction)
                renderer.draw_hud(env.score, env.level, record)

                label = renderer.font_tiny.render(
                    f"Episode {episode}/{episodes}  |  ε={agent.epsilon:.3f}", True, (150, 150, 180))
                renderer.screen.blit(label, (10, 580))

                renderer.update()
                renderer.flip()
                renderer.tick_clock(60)

        # batch replay at end of episode
        agent.train_long_memory()
        agent.decay_epsilon()
        agent.n_games += 1

        score = info["score"]
        total_score += score
        mean_score = total_score / episode
        scores.append(score)
        mean_scores.append(mean_score)

        if score > record:
            record = score
            agent.save(model_path)

        if episode % 10 == 0 or episode == 1:
            print(f"  Ep {episode:>4d}  |  Score: {score:>3d}  |  "
                  f"Record: {record:>3d}  |  Mean: {mean_score:>6.1f}  |  "
                  f"ε: {agent.epsilon:.3f}")

        if plot and episode % 10 == 0:
            try:
                plot_training(scores, mean_scores)
            except Exception:
                pass

    agent.save(model_path)
    print("-" * 50)
    print(f"  Training complete! Record score: {record}")
    print(f"  Model saved to {model_path}")

    if renderer:
        renderer.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Snake RL Agent")
    parser.add_argument("--episodes", type=int, default=500, help="Number of training episodes")
    parser.add_argument("--render", action="store_true", help="Show game during training")
    parser.add_argument("--no-plot", action="store_true", help="Disable live plotting")
    args = parser.parse_args()

    train(episodes=args.episodes, render=args.render, plot=not args.no_plot)
