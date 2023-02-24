# YAXT

YAXT installation requires MPI. At JSC, it is neccessary to have an active `salloc` session and to specify a buildpath. For example on JUWELS:
```
salloc --time=1:00:00 --nodes=1 --ntasks=16 --partition=devel -A cswmanage
eb YAXT-0.9.3.1-gpsmpi-2022a.eb --buildpath=/p/scratch/cswmanage/$USER/builddir/$SYSTEMNAME/
```