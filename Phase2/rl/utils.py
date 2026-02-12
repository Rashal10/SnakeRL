import matplotlib.pyplot as plt

def plot_training(scores, mean_scores, title="RL Snake Training"):
    plt.ion()
    plt.clf()
    plt.title(title)
    plt.xlabel("Episode")
    plt.ylabel("Score")
    plt.plot(scores, label="Score", alpha=0.6, color="cyan")
    plt.plot(mean_scores, label="Mean Score", color="lime", linewidth=2)
    if scores:
        plt.text(len(scores) - 1, scores[-1], str(scores[-1]),
                 fontsize=9, color="cyan")
        plt.text(len(mean_scores) - 1, mean_scores[-1],
                 f"{mean_scores[-1]:.1f}", fontsize=9, color="lime")
    plt.legend(loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.pause(0.05)
