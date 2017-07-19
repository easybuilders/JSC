The table below shows the details of the toolchains in the 2016b stage:

| Toolchain name |     Toolchain version     | Underlying GCC |     Compiler     |          MPI           |  CUDA  | Math libraries |    Includes software from     |                          Notes                           |
|----------------|---------------------------|----------------|------------------|------------------------|--------|----------------|-------------------------------|----------------------------------------------------------|
| GCCcore        | 5.4.0                     | 5.4.0          |                  |                        |        |                |                               | Used for boostrapping other compilers and basic software |
| GCC            | 5.4.0                     | 5.4.0          | GCC 5.4.0        |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| iccifort       | 2016.4.258-GCC-5.4.0      | 5.4.0          | Intel 2016.4.258 |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| iccifort       | 2017.0.098-GCC-5.4.0      | 5.4.0          | Intel 2017.0.098 |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| PGI            | 16.9-GCC-5.4.0            | 5.4.0          | PGI 16.9         |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| gpsmpi         | 2016b                     | 5.4.0          | GCC 5.4.0        | ParaStationMPI 5.1.5-1 |        |                | GCCcore, GCC                  | Compiler+MPI toolchain                                   |
| iimpi          | 2016b                     | 5.4.0          | Intel 2017.0.098 | IntelMPI 2017.0.098    |        |                | GCCcore, iccifort             | Compiler+MPI toolchain                                   |
| ipsmpi         | 2016b                     | 5.4.0          | Intel 2017.0.098 | ParaStationMPI 5.1.5-1 |        |                | GCCcore, iccifort             | Compiler+MPI toolchain                                   |
| gmvapich2c     | 2016b-GDR                 | 5.4.0          | GCC 5.4.0        | MVAPICH2 2.2-GDR       | 8.0.44 |                | GCCcore, GCC                  | Compiler+MPI+CUDA toolchain                              |
| imvapich2c     | 2016b-GDR                 | 5.4.0          | Intel 2016.4.258 | MVAPICH2 2.2-GDR       | 8.0.44 |                | GCCcore, iccifort             | Compiler+MPI+CUDA toolchain                              |
| pmvapich2c     | 2016b-GDR                 | 5.4.0          | PGI 16.9         | MVAPICH2 2.2-GDR       | 8.0.44 |                | GCCcore, PGI                  | Compiler+MPI+CUDA toolchain                              |
| gpsolf         | 2016b                     | 5.4.0          | GCC 5.4.0        | ParaStationMPI 5.1.5-1 |        | OLF 2016b      | GCCcore, GCC, gpsmpi          | Compiler+MPI+Math toolchain                              |
| intel-para     | 2016b                     | 5.4.0          | Intel 2017.0.098 | ParaStationMPI 5.1.5-1 |        | MKL 2017.0.098 | GCCcore, iccifort, ipsmpi     | Compiler+MPI+Math toolchain                              |
| intel          | 2016b                     | 5.4.0          | Intel 2017.0.098 | IntelMPI 5.1.3.181     |        | MKL 2017.0.098 | GCCcore, iccifort, iimpi      | Compiler+MPI+Math toolchain                              |
| gmvolfc        | 2016b-GDR                 | 5.4.0          | GCC 5.4.0        | MVAPICH2 2.2-GDR       | 8.0.44 | OLF 2016b      | GCCcore, GCC, gmvapich2c      | Compiler+MPI+CUDA+Math toolchain                         |
| imvmklc        | 2016b-GDR                 | 5.4.0          | Intel 2016.4.258 | MVAPICH2 2.2-GDR       | 8.0.44 | MKL 2017.0.098 | GCCcore, iccifort, imvapich2c | Compiler+MPI+CUDA+Math toolchain                         |
| pmvmklc        | 2016b-GDR                 | 5.4.0          | PGI 16.9         | MVAPICH2 2.2-GDR       | 8.0.44 | MKL 2017.0.098 | GCCcore, PGI, pmvapich2c      | Compiler+MPI+CUDA+Math toolchain                         |

*OLF 2016b: OpenBLAS 0.2.19, LAPACK 3.6.1, ScaLAPACK 2.0.2, FFTW 3.3.5
