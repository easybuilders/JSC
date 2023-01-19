# netCDF

The netCDF test is also running tests with MPI. On JSC, it is neccessary to have an active `salloc` session. For example:
```
salloc --time=2:00:00 --nodes=1 --ntasks=16 --partition=dc-cpu-devel-sw -A cswmanage
eb netCDF-4.9.0-gompi-2022a.eb eb --buildpath=/p/scratch/cswmanage/builddir/$SYSTEMNAME/
```
