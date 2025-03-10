# netcdf4-python

Tests and sanity checks require mpirun, which is not available in ParaStationMPI. Either switch off the tests in the eb file as we did in Stages/2022:
```
runtest = False  # mpirun problems
skipsteps = ['sanitycheck']  # mpirun problems
```

or use ```--mpi-cmd-template``` and also set 'PSP_CUDA="0"' as JUWELS-booster login nodes don't have GPUs, e.g.: 
```
eb --force --mpi-cmd-template='export PSP_CUDA="0" &&  echo %(nr_ranks)s && %(cmd)s' netcdf4-python-1.7.1.post2-ipsfbf-2024a.eb
```