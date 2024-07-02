# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
"""
Implementation of a hierarchical module naming scheme, with added flexibility

@author: Kenneth Hoste (Ghent University)
@author: Markus Geimer (Forschungszentrum Juelich GmbH)
@author: Alan O'Cais (Forschungszentrum Juelich GmbH)
@author: Damian Alvarez (Forschungszentrum Juelich GmbH)
"""

import os
import re
from easybuild.base import fancylogger

from easybuild.tools.build_log import EasyBuildError
from easybuild.tools.module_naming_scheme.hierarchical_mns import HierarchicalMNS
from easybuild.tools.module_naming_scheme.toolchain import det_toolchain_compilers, det_toolchain_mpi

CORE = 'Core'
COMPILER = 'Compiler'
MPI = 'MPI'
MPI_SETTINGS = 'MPI_settings'
PKG_SETTINGS = 'pkg_settings'

MODULECLASS_COMPILER = 'compiler'
MODULECLASS_MPI = 'mpi'
MODULECLASS_SIDECOMPILER = 'sidecompiler'

GCCCORE = 'GCCcore'

# note: names in keys are ordered alphabetically
COMP_NAME_VERSION_TEMPLATES = {
    'icc,ifort': ('intel', '%(icc)s'),
    'Clang,GCC': ('Clang-GCC', '%(Clang)s-%(GCC)s'),
    'CUDA,GCC': ('GCC-CUDA', '%(GCC)s-%(CUDA)s'),
    'xlc,xlf': ('xlcxlf', '%(xlc)s'),
}

# Compiler relevant version numbers
COMP_RELEVANT_VERSIONS = {
    'intel': 1,
    'intel-compilers': 1,
    'PGI': 1,
    'NVHPC': 1,
# The compilers load GCCcore/version. So GCC and GCCcore can't really be flexible, since GCCcore will always be loaded
# as a dependency with a full version, and GCC is nothing but a bundle around GCCcore + binutils
#    'GCC': 1,
#    'GCCcore': 1,
}

# Allow to reuse the stacks from other MPIs
SWAPPABLE_MPIS = {
    'BullMPI': ('OpenMPI', None),
    'impi': ('psmpi', '5'),
}

# MPI relevant version numbers
MPI_RELEVANT_VERSIONS = {
    'impi': 1,
    'psmpi': 1,
    'MVAPICH2': 2,
    'OpenMPI': 2,
    'BullMPI': 2,
}

# MPIs with settings modules
MPI_WITH_SETTINGS = ['psmpi', 'impi', 'OpenMPI', 'BullMPI']

# Communication packages with settings modules
PKG_WITH_SETTINGS = ['UCX', 'NCCL', 'LWP']

class FlexibleCustomHierarchicalMNS(HierarchicalMNS):
    """Class implementing an example hierarchical module naming scheme."""
    def is_short_modname_for(self, short_modname, name):
        """
        Determine whether the specified (short) module name is a module for software with the specified name.
        Default implementation checks via a strict regex pattern, and assumes short module names are of the form:
            <name>/<version>[-<toolchain>]
        """
        # We rename our iccifort compiler to INTEL and this needs a hard fix because it is a toolchain
        if name == 'iccifort' or name == 'intel-compilers':
            modname_regex = re.compile('^%s/\S+$' % re.escape('Intel'))
        elif name == 'psmpi':
            modname_regex = re.compile('^%s/\S+$' % re.escape('ParaStationMPI'))
        elif name == 'impi':
            modname_regex = re.compile('^%s/\S+$' % re.escape('IntelMPI'))
        elif name in ['-'.join([x, 'settings']) for x in MPI_WITH_SETTINGS]:
            modname_regex = re.compile('^%s/\S+$' % re.escape('MPI-settings'))
        elif name == 'LWP-settings':
            # Match almost anything, since the name depends actually on the version, to avoid load conflicts
            modname_regex = re.compile('^LWP-\S+/enable$')
        else:
            modname_regex = re.compile('^%s/\S+$' % re.escape(name))
        res = bool(modname_regex.match(short_modname))

        self.log.debug("Checking whether '%s' is a module name for software with name '%s' via regex %s: %s",
                       short_modname, name, modname_regex.pattern, res)

        return res

    def _find_relevant_compiler_info(self, comp_info):
        comp_name, comp_ver = comp_info

        # Strip the irrelevant bits of the version and append the suffix again
        if comp_name in COMP_RELEVANT_VERSIONS:
            suffix = '-'.join(comp_ver.split('-')[1:])
            comp_ver = '.'.join(comp_ver.split('.')[:COMP_RELEVANT_VERSIONS[comp_name]])
            if suffix:
                comp_ver += '-%s' % suffix

        return comp_name, comp_ver

    def _find_relevant_mpi_info(self, mpi_info):
        mpi_ver = self.det_full_version(mpi_info)
        mpi_name = mpi_info['name']

        # We'll start ignoring suffixes in MPI toolchains. But let's keep the code around for a bit, in case it needs
        # to be readded. Not elegant, I know, but digging up in git is always extra effort.

        # Find suffix, if any, to be appended. Try to be clever, since the suffix is embedded in the version
        # and sometimes the version might include a string that looks like a suffix (ie: psmpi-5.4.0-1)
        if mpi_name in MPI_RELEVANT_VERSIONS:
            # Find possible suffixes
            possible_suffixes = mpi_ver.split('-')[1:]
            suffix = ''
            # Match the '-1' that is a typical part of psmpi's version
            #if possible_suffixes:
            #    if re.match('^\d$', possible_suffixes[0]):
            #        suffix_index = 2
            #    else:
            #        suffix_index = 1
            #    suffix = '-'.join(mpi_ver.split('-')[suffix_index:])

            mpi_ver = '.'.join(mpi_ver.split('.')[:MPI_RELEVANT_VERSIONS[mpi_name]])
            if suffix:
                mpi_ver += '-%s' % suffix

        return mpi_name, mpi_ver

    def det_toolchain_compilers_name_version(self, tc_comps):
        """
        Determine toolchain compiler tag, for given list of compilers.
        """
        if tc_comps is None:
            # no compiler in toolchain, system toolchain
            res = None
        elif len(tc_comps) == 1:
            tc_comp = tc_comps[0]
            if tc_comp is None:
                res = None
            else:
                # Rename intel-compilers to intel, just to keep it consistent with installations pre oneAPI
                if tc_comp['name'] == 'intel-compilers':
                    tc_comp['name'] = 'intel'
                res = (tc_comp['name'], self.det_full_version(tc_comp))
        else:
            comp_versions = dict([(comp['name'], self.det_full_version(comp)) for comp in tc_comps])
            comp_names = comp_versions.keys()
            key = ','.join(sorted(comp_names))
            if key in COMP_NAME_VERSION_TEMPLATES:
                tc_comp_name, tc_comp_ver_tmpl = COMP_NAME_VERSION_TEMPLATES[key]
                tc_comp_ver = tc_comp_ver_tmpl % comp_versions
                # make sure that icc/ifort versions match (unless not existing as separate modules)
                if tc_comp_name == 'intel' and comp_versions.get('icc') != comp_versions.get('ifort'):
                    raise EasyBuildError("Bumped into different versions for Intel compilers: %s", comp_versions)
            else:
                raise EasyBuildError("Unknown set of toolchain compilers, module naming scheme needs work: %s",
                                     comp_names)
            res = (tc_comp_name, tc_comp_ver)
        return res

    def det_module_subdir(self, ec):
        """
        Determine module subdirectory, relative to the top of the module path.
        This determines the separation between module names exposed to users, and what's part of the $MODULEPATH.
        Examples: Core, Compiler/GCC/4.8.3, MPI/GCC/4.8.3/OpenMPI/1.6.5
        """
        tc_comps = det_toolchain_compilers(ec)
        tc_comp_info = self.det_toolchain_compilers_name_version(tc_comps)
        # determine prefix based on type of toolchain used
        if tc_comp_info is None:
            # no compiler in toolchain, dummy toolchain => Core module
            subdir = CORE
            # except if the module is a MPI settings module
            stripped_name = ec['name'].split('-settings')[0]
            if stripped_name in MPI_WITH_SETTINGS:
                subdir = os.path.join(MPI_SETTINGS, stripped_name, ec['version'])
            # or a module is for a package with settings
            elif (stripped_name in PKG_WITH_SETTINGS and '-settings' in ec['name']):
                subdir = os.path.join(PKG_SETTINGS, stripped_name)
        else:
            tc_comp_name, tc_comp_ver = self._find_relevant_compiler_info(tc_comp_info)
            tc_mpi = det_toolchain_mpi(ec)
            if tc_mpi is None:
                # compiler-only toolchain => Compiler/<compiler_name>/<compiler_version> namespace
                # but we want the mpi module class to stand alone
                if ec['moduleclass'] == MODULECLASS_MPI:
                    subdir = os.path.join(COMPILER, MODULECLASS_MPI, tc_comp_name, tc_comp_ver)
                elif ec['moduleclass'] == MODULECLASS_SIDECOMPILER:
                    subdir = os.path.join(COMPILER, MODULECLASS_SIDECOMPILER, tc_comp_name, tc_comp_ver)
                else:
                    subdir = os.path.join(COMPILER, tc_comp_name, tc_comp_ver)
            else:
                tc_mpi_name, tc_mpi_ver = self._find_relevant_mpi_info(tc_mpi)
                # compiler-MPI toolchain => MPI/<comp_name>/<comp_version>/<MPI_name>/<MPI_version> namespace
                subdir = os.path.join(MPI, tc_comp_name, tc_comp_ver, tc_mpi_name, tc_mpi_ver)

        return subdir

    def det_short_module_name(self, ec):
        """
        Determine short module name, i.e. the name under which modules will be exposed to users.
        Examples: GCC/4.8.3, OpenMPI/1.6.5, OpenBLAS/0.2.9, HPL/2.1, Python/2.7.5
                  MPI-settings/plain, etc
        """
        stripped_name = re.sub('-settings$', '', ec['name'])
        if stripped_name in MPI_WITH_SETTINGS and '-settings' in ec['name']:
            return os.path.join('MPI-settings', ec['versionsuffix'])
        elif stripped_name.startswith('LWP') and '-settings' in ec['name']:
            return os.path.join(ec['version'], 'enable')
        else:
            return super(FlexibleCustomHierarchicalMNS, self).det_short_module_name(ec)

    def det_modpath_extensions(self, ec):
        """
        Determine module path extensions, if any.
        Examples: Compiler/GCC/4.8.3 (for GCC/4.8.3 module), MPI/GCC/4.8.3/OpenMPI/1.6.5 (for OpenMPI/1.6.5 module)
        """
        modclass = ec['moduleclass']
        tc_comps = det_toolchain_compilers(ec)
        tc_comp_info = self.det_toolchain_compilers_name_version(tc_comps)

        paths = []
        if modclass == MODULECLASS_COMPILER or ec['name'] in ['iccifort']:
            # obtain list of compilers based on that extend $MODULEPATH in some way other than <name>/<version>
            extend_comps = []
            # exclude GCC for which <name>/<version> is used as $MODULEPATH extension
            excluded_comps = ['GCC']
            for comps in COMP_NAME_VERSION_TEMPLATES.keys():
                extend_comps.extend([comp for comp in comps.split(',') if comp not in excluded_comps])

            comp_name_ver = None
            if ec['name'] in extend_comps:
                for key in COMP_NAME_VERSION_TEMPLATES:
                    if ec['name'] in key.split(','):
                        comp_name, comp_ver_tmpl = COMP_NAME_VERSION_TEMPLATES[key]
                        comp_versions = {ec['name']: self.det_full_version(ec)}
                        if ec['name'] == 'ifort':
                            # 'icc' key should be provided since it's the only one used in the template
                            comp_versions.update({'icc': self.det_full_version(ec)})
                        if tc_comp_info is not None:
                            # also provide toolchain version for non-dummy toolchains
                            comp_versions.update({tc_comp_info[0]: tc_comp_info[1]})

                        comp_name_ver = [comp_name, comp_ver_tmpl % comp_versions]
                        break
            else:
                comp_name_ver = [ec['name'], self.det_full_version(ec)]
                # Handle the case where someone only wants iccifort to extend the path
                # This means icc/ifort are not of the moduleclass compiler but iccifort is
                if ec['name'] == 'iccifort' or ec['name'] == 'intel-compilers':
                    comp_name_ver = ['intel', self.det_full_version(ec)]

            # Exclude extending the path for icc/ifort, the iccifort special case is handled above
            if ec['name'] not in ['icc', 'ifort']:
                # Overwrite version if necessary
                comp_name_ver = self._find_relevant_compiler_info(comp_name_ver)

                # Hack the MNS here, so NVHPC 24 expands to the path of NVHPC 23, to reuse the stack there
                # NVIDIA stated in GTC2024 that they intend to keep ABI compatibility, and if they break it
                # it would be clearly announced. So for the next stage, we should generalize the modpath expansion
                # to "2X", instead of 23, 24, or whatever year we are on
                comp_name, comp_ver = comp_name_ver
                if comp_name == "NVHPC":
                    comp_name_ver = (comp_name, "23"+comp_ver[2:])

                paths.append(os.path.join(COMPILER, *comp_name_ver))
                # Always extend to capture the MPI implementations too (which are in a separate directory)
                if ec['name'] not in [GCCCORE]:
                    paths.append(os.path.join(COMPILER, MODULECLASS_MPI, *comp_name_ver))
                # Extend the MOODULEPATH to include the side compilers available in GCCcore
                else:
                    paths.append(os.path.join(COMPILER, MODULECLASS_SIDECOMPILER, *comp_name_ver))

        elif modclass == MODULECLASS_MPI:
            if tc_comp_info is None:
                raise EasyBuildError("No compiler available in toolchain %s used to install MPI library %s v%s, "
                                     "which is required by the active module naming scheme.",
                                     ec['toolchain'], ec['name'], ec['version'])
            else:
                tc_comp_name, tc_comp_ver = self._find_relevant_compiler_info(tc_comp_info)
                mpi_name, mpi_ver = self._find_relevant_mpi_info(ec)
                # Hack the module path extension, so BullMPI actually reuses the stack from OpenMPI
                # instead of building everything on top unnecessarily. Same for IntelMPI on top of ParaStationMPI
                # Note that both paths ("real" MPI and "base" MPI) are expanded. That means that we could
                # have name collisions if we are not careful. However, the usage of toolchains based on 
                # BullMPI or IntelMPI should be limited to very particular use cases, where packages
                # would not work with the "base" MPIs (ParaStationMPI, OpenMPI), so this situation should
                # simply not happen. If it does, the "real" MPI takes precedence.
                paths.append(os.path.join(MPI, tc_comp_name, tc_comp_ver, mpi_name, mpi_ver))
                if mpi_name in SWAPPABLE_MPIS:
                    paths.append(os.path.join(MPI, tc_comp_name, tc_comp_ver, SWAPPABLE_MPIS[mpi_name][0], SWAPPABLE_MPIS[mpi_name][1] or mpi_ver))

                if ec['name'] in MPI_WITH_SETTINGS:
                    paths.append(os.path.join(MPI_SETTINGS, mpi_name, mpi_ver))

        elif ec['name'] in PKG_WITH_SETTINGS:
            paths.append(os.path.join(PKG_SETTINGS, ec['name']))

        return paths
