# Custom EasyBlocks

Overview of the custom EasyBlocks.

## generic/SYSTEM_BUNDLE

- __*added by*__ d.alvarez
- __*needed because*__ it is the basic support for the MPI settings modules
- __*can not be removed*__

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
- __*needed because*__ want to use easyconfig parameters to determine CUDA capability.
- __*difference compared to upstream*__ upstream doesn't have such a feature
- __*can not be removed*__ until merged upstream

## hypre
- __*added_by*__ r.partzsch
- __*needed because*__ tbd
- __*difference compared to upstream*__ tbd
- __*can not be removed*__ tbd

## JULIA

- __*added by*__ j.goebbert
- __*needed because*__ we offer more functionality compared to upstream
- __*difference compared to upstream*__ upstream has not yet an EasyBlock for julia, juliabundle and juliapackage
- __*can not be removed*__ once merged with upstream

## MPICH

- __*added by*__ d.alvarez
- __*needed because*__ --with-thread-package=pthreads is added
- __*difference compared to upstream*__ the aforementioned parameter
- __*can not be removed*__ 

## NVIDIA_DRIVER

- __*added by*__ d.alvarez
- __*needed because*__ we custom-install the NVIDIA driver libraries in the EB stack
- __*can not be removed*__ at least until the easyblock is added upstream

## OPENMPI

- __*added by*__ s.achilles
- __*needed because*__ the check for `mpirun` should be optional
- __*difference compared to upstream*__ making that check optional
- __*can not be removed*__ until the check is made optional upstream (PR: [#2788](https://github.com/easybuilders/easybuild-easyblocks/pull/2788))

## petsc

- __*added by*__ r.partzsch
- __*needed because*__ tbd
- __*difference compared to upstream*__ tbd
- __*can not be removed*__ tbd

## sundials

- __*added by*__ r.partzsch
- __*needed because*__ tbd
- __*difference compared to upstream*__ tbd
- __*can not be removed*__ tbd

## torchvision

- __*added by*__ a.strube
- __*needed because*__ tbd
- __*difference compared to upstream*__ tbd
- __*can not be removed*__ tbd

## totalview

- __*added by*__ m.knobloch
- __*needed because*__ New EasyBlock supports Aarch64
- __*difference compared to upstream*__ support for Aarch64
- __*can not be removed*__ at least until that option is merged upstream

