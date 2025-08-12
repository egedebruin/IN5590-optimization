import concurrent.futures
import json
import os
import time

import numpy as np

from biped import biped
from quadruped import quadruped

RESTARTS = 10
MAX_EPISODES = 100
MAX_WITHOUT_IMPROVEMENT = 50
TYPE = 'quadruped'


def run_simulation(actions, render=False):
    if TYPE == 'quadruped':
        return quadruped.run(actions, render)
    elif TYPE == 'biped':
        return biped.run(actions, render)
    else:
        raise ValueError('Unknown simulation type')

def run_optimization(repetition):
    # Unique seed for each process
    seed = int(time.time() * 1000000) % (2**32) + os.getpid() + repetition
    np.random.seed(seed)

    print(f"Restart: {repetition + 1} (seed={seed})")

    if TYPE == 'quadruped':
        current = np.random.uniform(low=0, high=1, size=(24,))
    elif TYPE == 'biped':
        current = np.random.uniform(low=0, high=1, size=(6,))
    else:
        raise ValueError('Unknown simulation type')

    current_value = run_simulation(current)
    value_progression = [current_value]
    without_improvement = 0
    for episode in range(MAX_EPISODES):
        if TYPE == 'quadruped':
            noise = np.random.normal(loc=0.0, scale=0.1, size=(24,))
        elif TYPE == 'biped':
            noise = np.random.normal(loc=0.0, scale=0.1, size=(6,))
        new = np.clip(current + noise, 0, 1)
        new_value = run_simulation(new)

        without_improvement += 1
        if new_value > current_value:
            current = new
            current_value = new_value
            without_improvement = 0
        value_progression.append(current_value)

        if without_improvement >= MAX_WITHOUT_IMPROVEMENT:
            break

    print(f"Restart {repetition} best: {current_value}")

    return value_progression, current, seed



def main():
    with concurrent.futures.ProcessPoolExecutor(
            max_workers=10
    ) as executor:
        futures = []
        for repetition in range(RESTARTS):
            futures.append(executor.submit(run_optimization, repetition))

    results = []
    for future in futures:
        results.append(future.result())

    with open('files/results.json', 'w') as results_file:
        json.dump(
            [{"results": rep, "best_controller": controller.tolist(), "seed": seed}
             for rep, controller, seed in results],
            results_file, indent=4
        )
    # run_simulation(best_controller, True)

if __name__ == '__main__':
    main()