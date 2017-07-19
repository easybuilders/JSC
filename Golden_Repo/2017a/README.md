The table below shows the details of the toolchains in the 2017a stage:

| Toolchain name |     Toolchain version     | Underlying GCC |     Compiler     |          MPI           |  CUDA  | Math libraries |    Includes software from     |                          Notes                           |
|----------------|---------------------------|----------------|------------------|------------------------|--------|----------------|-------------------------------|----------------------------------------------------------|
| GCCcore        | 5.4.0                     | 5.4.0          |                  |                        |        |                |                               | Used for boostrapping other compilers and basic software |
| GCC            | 5.4.0                     | 5.4.0          | GCC 5.4.0        |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| iccifort       | 2016.4.258-GCC-5.4.0      | 5.4.0          | Intel 2016.4.258 |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| iccifort       | 2017.2.174-GCC-5.4.0      | 5.4.0          | Intel 2017.2.174 |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| PGI            | 17.3-GCC-5.4.0            | 5.4.0          | PGI 17.3         |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| gpsmpi         | 2017a                     | 5.4.0          | GCC 5.4.0        | ParaStationMPI 5.1.9-1 |        |                | GCCcore, GCC                  | Compiler+MPI toolchain                                   |
| iimpi          | 2017a                     | 5.4.0          | Intel 2017.2.174 | IntelMPI 2017.2.174    |        |                | GCCcore, iccifort             | Compiler+MPI toolchain                                   |
| ipsmpi         | 2017a                     | 5.4.0          | Intel 2017.2.174 | ParaStationMPI 5.1.9-1 |        |                | GCCcore, iccifort             | Compiler+MPI toolchain                                   |
| gmvapich2c     | 2017a-GDR                 | 5.4.0          | GCC 5.4.0        | MVAPICH2 2.2-GDR       | 8.0.61 |                | GCCcore, GCC                  | Compiler+MPI+CUDA toolchain                              |
| imvapich2c     | 2017a-GDR                 | 5.4.0          | Intel 2016.4.258 | MVAPICH2 2.2-GDR       | 8.0.61 |                | GCCcore, iccifort             | Compiler+MPI+CUDA toolchain                              |
| pmvapich2c     | 2017a-GDR                 | 5.4.0          | PGI 17.3         | MVAPICH2 2.2-GDR       | 8.0.61 |                | GCCcore, PGI                  | Compiler+MPI+CUDA toolchain                              |
| gpsolf         | 2017a                     | 5.4.0          | GCC 5.4.0        | ParaStationMPI 5.1.9-1 |        | OLF 2017a      | GCCcore, GCC, gpsmpi          | Compiler+MPI+Math toolchain                              |
| intel-para     | 2017a                     | 5.4.0          | Intel 2017.2.174 | ParaStationMPI 5.1.9-1 |        | MKL 2017.2.174 | GCCcore, iccifort, ipsmpi     | Compiler+MPI+Math toolchain                              |
| intel          | 2017a                     | 5.4.0          | Intel 2017.2.174 | IntelMPI 2017.2.174    |        | MKL 2017.2.174 | GCCcore, iccifort, iimpi      | Compiler+MPI+Math toolchain                              |
| gmvolfc        | 2017a-GDR                 | 5.4.0          | GCC 5.4.0        | MVAPICH2 2.2-GDR       | 8.0.61 | OLF 2017a      | GCCcore, GCC, gmvapich2c      | Compiler+MPI+CUDA+Math toolchain                         |
| imvmklc        | 2017a-GDR                 | 5.4.0          | Intel 2016.4.258 | MVAPICH2 2.2-GDR       | 8.0.61 | MKL 2017.2.174 | GCCcore, iccifort, imvapich2c | Compiler+MPI+CUDA+Math toolchain                         |
| pmvmklc        | 2017a-GDR                 | 5.4.0          | PGI 17.3         | MVAPICH2 2.2-GDR       | 8.0.61 | MKL 2017.2.174 | GCCcore, PGI, pmvapich2c      | Compiler+MPI+CUDA+Math toolchain                         |

*OLF 2017a: OpenBLAS 0.2.19, LAPACK 3.7.0, ScaLAPACK 2.0.2, FFTW 3.3.6
