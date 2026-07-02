# Custom EasyBlocks

Overview of the custom EasyBlocks.

## generic/SYSTEM_BUNDLE

- __*added by*__ d.alvarez
- __*needed because*__ it is the basic support for the MPI settings modules
- __*can not be removed*__

## generic/nvidiabase & nvidia_compilers

- __*added by*__ j.reuter
- __*needed because*__ Adds minor changes to better handle new `nvidia-compilers` toochain at JSC, not yet upstreamed
- __*difference compared to upstream*__ allow to still use internal components for `nvidia-compilers`, fix issue with CUDA versions (see [#4024](https://github.com/easybuilders/easybuild-easyblocks/pull/4024))
- __*can not be removed*__ until all changes are merged upstream

## allinea

- __*added by*__ s.achilles
- __*needed because*__ we need to allow multiple license files
- __*difference compared to upstream*__ the aforementioned parameter
- __*can not be removed*__ at least until that option is merged upstream

## CODE_SATURNE

- __*added by*__ m.cakircali
- __*needed because*__ there is no support to install `code_saturn` upstream
- __*can not be removed*__ at least until the easyblock is added upstream

## CP2K
- __*added_by*__ th.mueller
- __*needed because*__  support for libvori; alternative versions of dbcsr; contains loads of widely obsolete stuff; is  essentially a highly non-portable easyblock working only with intel and gnu (which I am not going to change!); running the tests will not work within an eb environment - at least not sensibly. 
- __*difference compared to upstream*__ no support for libvori 
- __*can not be removed*__

## CPMD
- __*added_by*__ th.mueller
- __*needed because*__  tbd
- __*difference compared to upstream*__ tbd
- __*can not be removed*__

## ELPA
- __*added_by*__ d.alvarez
- __*needed because*__ to autodetect CUDA and support CUDA compute capabilities
- __*difference compared to upstream*__ upstream doesn't have such a feature
- __*can not be removed*__ until merged upstream (https://github.com/easybuilders/easybuild-easyblocks/pull/2673)

## GROMACS
- __*added_by*__ j.meinke
- __*needed because*__ allow to optionally disable Python package
- __*difference compared to upstream*__ upstream doesn't have such a feature
- __*can not be removed*__ until merged upstream

## HYPRE
- __*added_by*__ r.partzsch
- __*needed because*__ allow to optionally disable CUDA
- __*difference compared to upstream*__ upstream doesn't have such feature
- __*can not be removed*__ until merged upstream

## Julia, JuliaPackage & JuliaBundle

- __*added by*__ j.goebbert
- __*needed because*__ different approaches to handling Julia and its packages, needs unification
- __*difference compared to upstream*__ upstream does not have an EasyBlock for Julia, and its generic EasyBlocks for JuliaPackge and JuliaBundle differ significantly.
- __*can not be removed*__ once upstream approach has been evaluated and decided if we want to upstream our efforts

## Libint

- __*added by*__ th.mueller
- __*needed because*__ Optionally remove C++ interface (from 2.11 onwards) and ensure shared library builds
- __*difference compared to upstream*__ Added CMake flags and additional option with_cxx
- __*can not be removed*__ until upstreamed

## MPICH

- __*added by*__ d.alvarez
- __*needed because*__ --with-thread-package=pthreads is added
- __*difference compared to upstream*__ the aforementioned parameter
- __*can not be removed*__ 

## NVIDIA_DRIVER

- __*added by*__ d.alvarez
- __*needed because*__ we custom-install the NVIDIA driver libraries in the EB stack
- __*can not be removed*__ at least until the easyblock is added upstream

## OpenMPI

- __*added by*__ s.achilles
- __*needed because*__ the check for `mpirun` should be optional
- __*difference compared to upstream*__ making that check optional
- __*can not be removed*__ until the check is made optional upstream (PR: [#2788](https://github.com/easybuilders/easybuild-easyblocks/pull/2788))

## sundials

- __*added by*__ r.partzsch
- __*needed because*__ tbd
- __*difference compared to upstream*__ tbd
- __*can not be removed*__ tbd

## totalview

- __*added by*__ m.knobloch
- __*needed because*__ not available upstream
- __*difference compared to upstream*__ not available upstream
- __*can not be removed*__ at least until merged upstream

## extrae

- __*added by*__ j.reuter
- __*needed because*__ changes not yet in EasyBuild release
- __*difference compared to upstream*__ support for additional libraries
- __*can not be removed*__ until EasyBuild v5.2.1/v5.3.0

## psmpi

- __*added by*__ j.reuter
- __*needed because*__ LLVM is not supported upstream yet
- __*difference compared to upstream*__ support for LLVM
- __*can not be removed*__ until https://github.com/easybuilders/easybuild-easyblocks/pull/4047 is merged

## score_p

- __*added by*__ j.reuter
- __*needed because*__ reworked easyblock for version v10.0
- __*difference compared to upstream*__ updated easyblock not part of EasyBuild v5.3.1
- __*can not be removed*__ until https://github.com/easybuilders/easybuild-easyblocks/pull/4133 has been merged
