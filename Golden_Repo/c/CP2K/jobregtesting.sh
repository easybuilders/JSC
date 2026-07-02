#!/bin/bash  
#SBATCH --account=<xxxxxx>
#SBATCH --nodes=1
#SBATCH --output=mpi-out.%j
#SBATCH --error=mpi-err.%j
#SBATCH --partition=<xxxxxx> 
#SBATCH --time=01:00:00


# replace all strings <xxxxxx> by appropriate values 

ml Stages/2026
ml GCC/14.3.0 
# either OpenMPI or parastation mpi version
#ml ParaStationMPI/5.13.0-1-mt
#ml OpenMPI/5.0.8
ml CP2K/2025.2

# supply an absolute path
SCRATCHDIR=<xxxxxx>
if [ ! -d $SCRATCHDIR ]; then
	mkdir -p $SCRATCHDIR
fi
cd $SCRATCHDIR
tar -xzf $EBROOTCP2K/tests/tests.tar.gz 
tar -xzf $EBROOTCP2K/tests/regtestingtools.tar.gz
tar -xzf $EBROOTCP2K/tests/gridtests.tar.gz
cd $SCRATCHDIR/tests

#  maxtasks * ompthreads* mpiranks  <= number of physical cores per node 
#  this runs 4601 short tests within about 20-30 minutes on a single node of jureca_dc

ncore=`cat /proc/cpuinfo  | grep 'cpu cores' | wc -l`
nphyscore=$((ncore/2))
maxtask1=$((nphyscore/2))
maxtask2=$((nphyscore/4))

echo "testing pure MPI mode maxtasks=$maxtask1 ..." 
./do_regtest.py  --mpiranks 2 --ompthreads 1 --maxtasks $maxtask1 --num_gpus 0 --timeout 400  \
	         --mpiexec "srun -A slchem --exclusive --ntasks={N} --threads-per-core=1 --cpus-per-task=1 --unbuffered " \
                --workbasedir $SCRATCHDIR  $EBROOTCP2K/bin psmp   >  $SCRATCHDIR/output.pure_mpi

tail -11 $SCRATCHDIR/output.pure_mpi

echo "testing hybrid MPI/OpenMP mode maxtasks=$maxtask2 ..."

./do_regtest.py  --mpiranks 2 --ompthreads 2 --maxtasks $maxtask2 --num_gpus 0 --timeout 400  \
	         --mpiexec "srun -A slchem --exclusive --ntasks={N} --threads-per-core=1 --cpus-per-task=2  --unbuffered " \
                 --workbasedir $SCRATCHDIR $EBROOTCP2K/bin psmp > $SCRATCHDIR/output.hybrid_mpiomp 

tail -11 $SCRATCHDIR/output.hybrid_mpiomp
