# Custom EasyBlocks

Overview of the custom EasyBlocks.

## allinea

- __*added by*__ s.achilles
- __*needed because*__ we need to allow multiple license files
- __*difference compared to upstream*__ the aforementioned parameter
- __*can not be removed*__ at least until that option is merged upstream

## CUDA

- __*added by*__ s.achilles
- __*needed because*__ the new easyblocks removes the stubs
- __*difference compared to upstream*__ the aforementioned parameter
- __*can not be removed*__ until we update to EB 4.8.1 which contains [PR #2793](https://github.com/easybuilders/easybuild-easyblocks/pull/2793)

## MPICH

- __*added by*__ d.alvarez
- __*needed because*__ optional `check_static_libs` parameter in the sanity check (used with `psmpi.py`)
- __*difference compared to upstream*__ the aforementioned parameter
- __*can not be removed*__ at least until that option (needed just for `psmpi.py`) is merged upstream (PR: #2787)

## PSMPI

- __*added by*__ d.alvarez
- __*needed because*__ CUDA support
- __*difference compared to upstream*__ the supporting code to enable CUDA support
- __*can not be removed*__ until the CUDA options are pushed upstream (PR: #2787)

## OPENMPI

- __*added by*__ d.alvarez
- __*needed because*__ the check for `mpirun` should be optional
- __*difference compared to upstream*__ making that check optional
- __*can not be removed*__ until the check is made optional upstream (PR: #2788)

## CODE_SATURNE

- __*added by*__ m.cakircali
- __*needed because*__ there is no support to install `code_saturn` upstream
- __*can not be removed*__ at least until the easyblock is added upstream

## NVIDIA_DRIVER

- __*added by*__ d.alvarez
- __*needed because*__ we custom-install the NVIDIA driver libraries in the EB stack
- __*can not be removed*__ at least until the easyblock is added upstream

## generic/SYSTEM_BUNDLE

- __*added by*__ d.alvarez
- __*needed because*__ it is the basic support for the MPI settings modules
- __*can not be removed*__

## SUITESPARSE

- __*added by*__ d.alvarez
- __*needed because*__ added CUDA-related tweaks not present in upstream
- __*difference compared to upstream*__ the aforementioned
- __*can not be removed*__ Once the PR is merged upstream. Hopefully with the next release

## JULIA

- __*added by*__ j.goebbert
- __*needed because*__ we offer more functionality compared to upstream
- __*difference compared to upstream*__ upstream has not yet an EasyBlock for julia, juliabundle and juliapackage
- __*can not be removed*__ once merged with upstream

## VMD
- __*added by*__ j.goebbert
- __*needed because*__ we replaced the Mesa module by our own OpenGL module compared to upstream
- __*difference compared to upstream*__ upstream checks for Mesa inside the easyblock
- __*can not be removed*__ once upstream uses our OpenGL module

## GROMACS
- __*added_by*__ j.meinke
- __*needed because*__ want to use easyconfig parameters to determine CUDA capability.
- __*difference compared to upstream*__ upstream doesn't have such a feature
- __*can not be removed*__ until merged upstream

## LAMMPS
- __*added_by*__ d.alvarez
- __*needed because*__ upstream does not include the changes that we used in the latest stage
- __*difference compared to upstream*__ various, done by Alan
- __*can not be removed*__ until merged upstream or the changes here are deprecated (need to be assesed by an expert)

## NAMD
- __*added_by*__ d.alvarez
- __*needed because*__ need to disable CUDA support even if CUDA comes as a dependency
- __*difference compared to upstream*__ upstream doesn't have such a feature
- __*can not be removed*__ until merged upstream

## ELPA
- __*added_by*__ d.alvarez
- __*needed because*__ to autodetect CUDA and support CUDA compute capabilities
- __*difference compared to upstream*__ upstream doesn't have such a feature
- __*can not be removed*__ until merged upstream (https://github.com/easybuilders/easybuild-easyblocks/pull/2673)

## CP2K
- __*added_by*__ th.mueller
- __*needed because*__  support for libvori; alternative versions of dbcsr; contains loads of widely obsolete stuff; is  essentially a highly non-portable easyblock working only with intel and gnu (which I am not going to change!); running the tests will not work within an eb environment - at least not sensibly. 
- __*difference compared to upstream*__ no support for libvori 
- __*can not be removed*__
