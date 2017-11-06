The table below shows the details of the toolchains in the 2017b stage:

| Toolchain name |     Toolchain version     | Underlying GCC |     Compiler     |          MPI           |  CUDA  | Math libraries |    Includes software from     |                          Notes                           |
|----------------|---------------------------|----------------|------------------|------------------------|--------|----------------|-------------------------------|----------------------------------------------------------|
| GCCcore        | 5.4.0                     | 5.4.0          |                  |                        |         |                |                               | Used for boostrapping other compilers and basic software |
| GCCcore        | 7.2.0                     | 7.2.0          |                  |                        |         |                |                               | Used for boostrapping other compilers and basic software |
| GCC            | 5.4.0                     | 5.4.0          | GCC 5.4.0        |                        |         |                | GCCcore                       | Compiler toolchain                                       |
| GCC            | 7.2.0                     | 7.2.0          | GCC 7.2.0        |                        |         |                | GCCcore                       | Compiler toolchain                                       |
| iccifort       | 2017.5.239-GCC-5.4.0      | 5.4.0          | Intel 2017.5.239 |                        |         |                | GCCcore                       | Compiler toolchain                                       |
| iccifort       | 2018.0.128-GCC-5.4.0      | 5.4.0          | Intel 2018.0.128 |                        |         |                | GCCcore                       | Compiler toolchain                                       |
| PGI            | 17.9-GCC-5.4.0            | 5.4.0          | PGI 17.9         |                        |         |                | GCCcore                       | Compiler toolchain                                       |
| gpsmpi         | 2017b                     | 7.2.0          | GCC 7.2.0        | ParaStationMPI 5.2.0-1 |         |                | GCCcore, GCC                  | Compiler+MPI toolchain                                   |
| iimpi          | 2017b                     | 5.4.0          | Intel 2018.0.128 | IntelMPI 2018.0.128    |         |                | GCCcore, iccifort             | Compiler+MPI toolchain                                   |
| ipsmpi         | 2017b                     | 5.4.0          | Intel 2018.0.128 | ParaStationMPI 5.2.0-1 |         |                | GCCcore, iccifort             | Compiler+MPI toolchain                                   |
| gmvapich2c     | 2017b-GDR                 | 5.4.0          | GCC 5.4.0        | MVAPICH2 2.3a-GDR      | 9.0.176 |                | GCCcore, GCC                  | Compiler+MPI+CUDA toolchain                              |
| imvapich2c     | 2017b-GDR                 | 5.4.0          | Intel 2017.5.239 | MVAPICH2 2.3a-GDR      | 9.0.176 |                | GCCcore, iccifort             | Compiler+MPI+CUDA toolchain                              |
| pmvapich2c     | 2017b-GDR                 | 5.4.0          | PGI 17.9         | MVAPICH2 2.3a-GDR      | 9.0.176 |                | GCCcore, PGI                  | Compiler+MPI+CUDA toolchain                              |
| gpsolf         | 2017b                     | 7.2.0          | GCC 7.2.0        | ParaStationMPI 5.2.0-1 |         | OLF 2017b      | GCCcore, GCC, gpsmpi          | Compiler+MPI+Math toolchain                              |
| intel-para     | 2017b                     | 5.4.0          | Intel 2018.0.128 | ParaStationMPI 5.2.0-1 |         | MKL 2018.0.128 | GCCcore, iccifort, ipsmpi     | Compiler+MPI+Math toolchain                              |
| intel          | 2017b                     | 5.4.0          | Intel 2018.0.128 | IntelMPI 2018.0.128    |         | MKL 2018.0.128 | GCCcore, iccifort, iimpi      | Compiler+MPI+Math toolchain                              |
| gmvolfc        | 2017b-GDR                 | 5.4.0          | GCC 5.4.0        | MVAPICH2 2.3a-GDR      | 9.0.176 | OLF 2017b      | GCCcore, GCC, gmvapich2c      | Compiler+MPI+CUDA+Math toolchain                         |
| imvmklc        | 2017b-GDR                 | 5.4.0          | Intel 2017.5.239 | MVAPICH2 2.3a-GDR      | 9.0.176 | MKL 2018.0.128 | GCCcore, iccifort, imvapich2c | Compiler+MPI+CUDA+Math toolchain                         |
| pmvmklc        | 2017b-GDR                 | 5.4.0          | PGI 17.9         | MVAPICH2 2.3a-GDR      | 9.0.176 | MKL 2018.0.128 | GCCcore, PGI, pmvapich2c      | Compiler+MPI+CUDA+Math toolchain                         |

*OLF 2017b: OpenBLAS 0.2.20, LAPACK 3.7.1, ScaLAPACK 2.0.2, FFTW 3.3.6
