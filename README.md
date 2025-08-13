## How to run on ROBIN-HPC
Tested on ROBIN-HPC, but you can probably use some things here to make it run locally as well.

### Create conda environment
We need python3.10 specifically, I did not test it with other version and it might break.
```
conda create -n <ENV_NAME> python=3.10
conda activate <ENV_NAME>
```

Don't forget to update `./example.sbatch` with the correct <ENV_NAME>.

### Download code and install requirements
```
git clone https://github.com/egedebruin/IN5590-optimization.git
cd IN5590-optimization
pip install -r requirements.txt
```

### Push optimization job to queue
```
sbatch example.sbatch
```

### Run optimization directly
```
python optimization.py --type='biped/quadruped'
```