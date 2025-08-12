import json

import matplotlib.pyplot as plt
import numpy as np

FILE = 'files/results.json'

def main():
    data = json.load(open(FILE))
    all_results = [item["results"] for item in data]
    best_repetition = np.argmax([max(rep) for rep in all_results])
    max_length = max(len(rep) for rep in all_results)
    padded = np.full((len(all_results), max_length), np.nan)

    for i, rep in enumerate(all_results):
        padded[i, :len(rep)] = rep

    mean = np.nanmean(padded, axis=0)
    best_rep_padded = np.pad(all_results[best_repetition], (0, max_length - len(all_results[best_repetition])), mode='constant', constant_values=np.nan)
    p25 = np.nanpercentile(padded, 25, axis=0)
    p75 = np.nanpercentile(padded, 75, axis=0)

    episodes = np.arange(max_length)

    plt.figure(figsize=(8, 5))
    plt.plot(episodes, mean, label="Mean objective", color='blue')
    plt.fill_between(episodes, p25, p75, alpha=0.3, label="25–75% percentile", color='blue')
    plt.plot(episodes, best_rep_padded, label="Best run", linestyle='--', color='blue')
    plt.xlabel("Episode")
    plt.ylabel("Objective value")
    plt.title("Episode progression averaged over repetitions")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()