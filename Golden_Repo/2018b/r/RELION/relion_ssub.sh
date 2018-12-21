#!/bin/bash -x
#SBATCH --ntasks=XXXmpinodesXXX
#SBATCH --ntasks-per-node=XXXextra2XXX
#SBATCH --cpus-per-task=XXXthreadsXXX
#SBATCH --time=XXXextra1XXX:00:00
#SBATCH --partition=XXXqueueXXX

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
srun XXXcommandXXX
