#!/bin/bash
#SBATCH --job-name=bayesopt_array
#SBATCH --output=logs/job_%A_%a.out
#SBATCH --error=logs/job_%A_%a.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=120:00:00
#SBATCH --mem-per-cpu=1G
#SBATCH --array=0-9

# Load environment
conda activate myenv

# Run the task
srun --ntasks=1 --cpus-per-task=10 python optimization.py --type="BIPED"
