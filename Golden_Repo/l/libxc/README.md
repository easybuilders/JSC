# libxc

The default version of `libxc` in the stage `2020` is `4.3.4`. We decided against the newer version `libxc/5.0.0`, as some applications would need to be patched. However, also not every application is working with version `4.3.4`, as the API changed between version 3 and 4. This lead to the fact that we need two different version:

- `libxc/3.0.1`
- `libxc/4.3.4`

Both versions are installed for the following toolchains:

- `GCC/9.3.0`
- `iccifort-2020.2.254-GCC-9.3.0`

## ABINIT

`ABINIT/8.X` is only working with `libxc/3.0.1` due to changes in the API. Starting with `ABINIT/9.X` version 4.3.0 or later is supported.

## Quantum ESPRESSO

While Quantum ESPRESSO 6.6 would work with `libxc/5.0.0`, QE would require a patch. From the Quantum ESPRESSO User Guide (https://www.quantum-espresso.org/Doc/user_guide.pdf):

**Note  for  version  5.0.0:** the `f03` interfaces  are  no  longer  available  in `libxc` 5.0.0. They have been reintroduced in the current develop version.  Version 5.0.0 is still usable, but, before compiling Quantum ESPRESSO, a string replacement is necessary, namely `‘xcf03’` must berepalced with `‘xcf90’` everywhere in the following files: `funct.f90, xcldalsdadrivers.f90, xcggadrivers.f90, xcmggadrivers.f90, dmxcdrivers.f90` and `dgcxcdrivers.f90` in `Modules` folder and `xctestqelibxc.f90` in `PP/src` folder.

## Note for future Stage 2021

Check if all application can work with the newest version of `libxc`, e.g. 5.0.0. One common version would be desirable.
