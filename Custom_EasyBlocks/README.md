# Custom EasyBlocks

Overview of the custom EasyBlocks.

## allinea

- __*added by*__ s.achilles
- __*needed because*__ we need to allow multiple license files
- __*difference compared to upstream*__ the aforementioned parameter
- __*can not be removed*__ at least until that option is merged upstream

## MPICH

- __*added by*__ d.alvarez
- __*needed because*__ optional `check_static_libs` parameter in the sanity check (used with `psmpi.py`)
- __*difference compared to upstream*__ the aforementioned parameter
- __*can not be removed*__ until EasyBuild 4.9.3 becomes available

## PSMPI

- __*added by*__ d.alvarez
- __*needed because*__ changes in options passed to configure
- __*difference compared to upstream*__ the supporting code to enable threading and MSA support in 5.10.0-1
- __*can not be removed*__ until these options are accepted upstream (PR: [#3420](https://github.com/easybuilders/easybuild-easyblocks/pull/3420))

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

## JULIA

- __*added by*__ j.goebbert
- __*needed because*__ we offer more functionality compared to upstream
- __*difference compared to upstream*__ upstream has not yet an EasyBlock for julia, juliabundle and juliapackage
- __*can not be removed*__ once merged with upstream

## GROMACS
- __*added_by*__ j.meinke
- __*needed because*__ want to use easyconfig parameters to determine CUDA capability.
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

## LLVM
- __*added by*__ j.reuter
- __*needed because*__ added support for NVPTX target if CUDA compute capabilities are set. This allows users to use JIT for example.
- __*difference compared to upstream*__ upstream version only sets host architecture if `build_targets` are not manually passed.
- __*can not be removed*__ until EasyBlock is changed to more general one (https://github.com/easybuilders/easybuild-easyblocks/pull/3373), or this change is upstreamed.

## AOCC
- __*added by*__ j.reuter
- __*needed because*__ AOCC 4.1.0 and newer are based on LLVM 16.0.3, which cannot be handled by EasyBlock in 4.9.4. EasyBlock fails sanity check due to incorrect paths. Also, compilers are not configured correctly starting with AOCC 4.2.0.
- __*difference compared to upstream*__ None, copied from PR https://github.com/easybuilders/easybuild-easyblocks/pull/3480 and https://github.com/easybuilders/easybuild-easyblocks/pull/3458
- __*can not be removed*__ until next EasyBuild release (after 4.9.4)

