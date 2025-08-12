import json
import numpy as np

from optimization import run_simulation

FILE = 'files/results.json'

def main():
    data = json.load(open(FILE))
    all_results = [item["results"] for item in data]
    best_repetition = np.argmax([max(rep) for rep in all_results])

    best_controller = data[best_repetition]['best_controller']
    run_simulation(best_controller, True)

if __name__ == '__main__':
    main()