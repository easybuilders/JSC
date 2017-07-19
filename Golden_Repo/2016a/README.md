The table below shows the details of the toolchains in the 2016a stage:

| Toolchain name |     Toolchain version     | Underlying GCC |     Compiler     |          MPI           |  CUDA  | Math libraries |    Includes software from     |                          Notes                           |
|----------------|---------------------------|----------------|------------------|------------------------|--------|----------------|-------------------------------|----------------------------------------------------------|
| GCCcore        | 4.9.3                     | 4.9.3          |                  |                        |        |                |                               | Used for boostrapping other compilers and basic software |
| GCCcore        | 5.3.0                     | 5.3.0          |                  |                        |        |                |                               | Used for boostrapping other compilers and basic software |
| GCC            | 4.9.3-2.25                | 4.9.3          | GCC 4.9.3        |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| GCC            | 5.3.0-2.26                | 5.3.0          | GCC 5.3.0        |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| iccifort       | 2016.2.181-GCC-4.9.3-2.25 | 4.9.3          | Intel 2016.2.181 |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| PGI            | 16.3-GCC-4.9.3-2.25       | 4.9.3          | PGI 16.3         |                        |        |                | GCCcore                       | Compiler toolchain                                       |
| gpsmpi         | 2016a                     | 5.3.0          | GCC 5.3.0        | ParaStationMPI 5.1.5-1 |        |                | GCCcore, GCC                  | Compiler+MPI toolchain                                   |
| iimpi          | 8.2.5-GCC-4.9.3-2.25      | 4.9.3          | Intel 2016.2.181 | IntelMPI 5.1.3.181     |        |                | GCCcore, iccifort             | Compiler+MPI toolchain                                   |
| ipsmpi         | 2016a                     | 4.9.3          | Intel 2016.2.181 | ParaStationMPI 5.1.5-1 |        |                | GCCcore, iccifort             | Compiler+MPI toolchain                                   |
| gmvapich2c     | 2016a-GDR                 | 4.9.3          | GCC 4.9.3        | MVAPICH2 2.2b-GDR      | 7.5.18 |                | GCCcore, GCC                  | Compiler+MPI+CUDA toolchain                              |
| imvapich2c     | 2016a-GDR                 | 4.9.3          | Intel 2016.2.181 | MVAPICH2 2.2b-GDR      | 7.5.18 |                | GCCcore, iccifort             | Compiler+MPI+CUDA toolchain                              |
| pmvapich2c     | 2016a-GDR                 | 4.9.3          | PGI 16.3         | MVAPICH2 2.2b-GDR      | 7.5.18 |                | GCCcore, PGI                  | Compiler+MPI+CUDA toolchain                              |
| gpsolf         | 2016a                     | 5.3.0          | GCC 5.3.0        | ParaStationMPI 5.1.5-1 |        | OLF 2016a      | GCCcore, GCC, gpsmpi          | Compiler+MPI+Math toolchain                              |
| intel-para     | 2016a                     | 4.9.3          | Intel 2016.2.181 | ParaStationMPI 5.1.5-1 |        | MKL 11.3.2-181 | GCCcore, iccifort, ipsmpi     | Compiler+MPI+Math toolchain                              |
| intel          | 2016a                     | 4.9.3          | Intel 2016.2.181 | IntelMPI 5.1.3.181     |        | MKL 11.3.2-181 | GCCcore, iccifort, iimpi      | Compiler+MPI+Math toolchain                              |
| gmvolfc        | 2016a-GDR                 | 4.9.3          | GCC 4.9.3        | MVAPICH2 2.2b-GDR      | 7.5.18 | OLF 2016a      | GCCcore, GCC, gmvapich2c      | Compiler+MPI+CUDA+Math toolchain                         |
| imvmklc        | 2016a-GDR                 | 4.9.3          | Intel 2015.3.187 | MVAPICH2 2.2b-GDR      | 7.5.18 | MKL 11.3.2-181 | GCCcore, iccifort, imvapich2c | Compiler+MPI+CUDA+Math toolchain                         |
| pmvmklc        | 2016a-GDR                 | 4.9.3          | PGI 16.3         | MVAPICH2 2.2b-GDR      | 7.5.18 | MKL 11.3.2-181 | GCCcore, PGI, pmvapich2c      | Compiler+MPI+CUDA+Math toolchain                         |

*OLF 2016a: OpenBLAS 0.2.15, LAPACK 3.6.0, ScaLAPACK 2.0.2, FFTW 3.3.4
