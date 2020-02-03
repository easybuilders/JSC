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

MODULECLASS_COMPILER = 'compiler'
MODULECLASS_MPI = 'mpi'

GCCCORE = 'GCCcore'

# note: names in keys are ordered alphabetically
COMP_NAME_VERSION_TEMPLATES = {
    'icc,ifort': ('intel', '%(icc)s'),
    'Clang,GCC': ('Clang-GCC', '%(Clang)s-%(GCC)s'),
    'CUDA,GCC': ('GCC-CUDA', '%(GCC)s-%(CUDA)s'),
    'xlc,xlf': ('xlcxlf', '%(xlc)s'),
}

# Compiler relevant version numbers
comp_relevant_versions = {
    'Intel': 1,
    'PGI': 1,
    'GCC': 1,
    'GCCcore': 1,
}

# MPI relevant version numbers
mpi_relevant_versions = {
    'impi': 1,
    'psmpi': 2,
    'MVAPICH2': 2,
    'OpenMPI': 2,
}

class FlexibleCustomHierarchicalMNS(HierarchicalMNS):
    """Class implementing an example hierarchical module naming scheme."""
    def is_short_modname_for(self, short_modname, name):
        """
        Determine whether the specified (short) module name is a module for software with the specified name.
        Default implementation checks via a strict regex pattern, and assumes short module names are of the form:
            <name>/<version>[-<toolchain>]
        """
        # We rename our iccifort compiler to INTEL and this needs a hard fix because it is a toolchain
        if name == 'iccifort':
            modname_regex = re.compile('^%s/\S+$' % re.escape('Intel'))
        elif name == 'psmpi':
            modname_regex = re.compile('^%s/\S+$' % re.escape('ParaStationMPI'))
        elif name == 'impi':
            modname_regex = re.compile('^%s/\S+$' % re.escape('IntelMPI'))
        else:
            modname_regex = re.compile('^%s/\S+$' % re.escape(name))
        res = bool(modname_regex.match(short_modname))

        self.log.debug("Checking whether '%s' is a module name for software with name '%s' via regex %s: %s",
                       short_modname, name, modname_regex.pattern, res)

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
        else:
            tc_comp_name, tc_comp_ver = tc_comp_info

            # Strip the irrelevant bits of the version and append the suffix again
            if comp_relevant_versions.has_key(tc_comp_name):
                suffix = '-'.join(tc_comp_ver.split('-')[1:])
                tc_comp_ver = '.'.join(tc_comp_ver.split('.')[:comp_relevant_versions[tc_comp_name]])
                if suffix:
                    tc_comp_ver += '-%s' % suffix

            tc_mpi = det_toolchain_mpi(ec)
            if tc_mpi is None:
                # compiler-only toolchain => Compiler/<compiler_name>/<compiler_version> namespace
                # but we want the mpi module class to stand alone
                if ec['moduleclass'] == MODULECLASS_MPI:
                    subdir = os.path.join(COMPILER, MODULECLASS_MPI, tc_comp_name, tc_comp_ver)
                else:
                    subdir = os.path.join(COMPILER, tc_comp_name, tc_comp_ver)
            else:
                tc_mpi_fullver = self.det_full_version(tc_mpi)

                # Find suffix, if any, to be appended. Try to be clever, since the suffix is embedded in the version
                # and sometimes the version might include a string that looks like a suffix (ie: psmpi-5.4.0-1)
                if mpi_relevant_versions.has_key(tc_mpi['name']):
                    # Match the '-1' that is a typical part of psmpi's version
                    if re.match('^\d$', tc_mpi_fullver.split('-')[1:][0]):
                        suffix_index = 2
                    else:
                        suffix_index = 1
                    suffix = '-'.join(tc_mpi_fullver.split('-')[suffix_index:])
                    tc_mpi_fullver = '.'.join(tc_mpi_fullver.split('.')[:mpi_relevant_versions[tc_mpi['name']]])
                    if suffix:
                        tc_mpi_fullver += '-%s' % suffix

                # compiler-MPI toolchain => MPI/<comp_name>/<comp_version>/<MPI_name>/<MPI_version> namespace
                subdir = os.path.join(MPI, tc_comp_name, tc_comp_ver, tc_mpi['name'], tc_mpi_fullver)

        return subdir

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
                if ec['name'] == 'iccifort':
                    comp_name_ver = ['intel', self.det_full_version(ec)]
            # Exclude extending the path for icc/ifort, the iccifort special case is handled above
            if ec['name'] not in ['icc', 'ifort']:
                paths.append(os.path.join(COMPILER, *comp_name_ver))
                # Always extend to capture the MPI implementations too (which are in a separate directory)
                if ec['name'] not in [GCCCORE]:
                    paths.append(os.path.join(COMPILER, MODULECLASS_MPI, *comp_name_ver))
        elif modclass == MODULECLASS_MPI:
            if tc_comp_info is None:
                raise EasyBuildError("No compiler available in toolchain %s used to install MPI library %s v%s, "
                                     "which is required by the active module naming scheme.",
                                     ec['toolchain'], ec['name'], ec['version'])
            else:
                tc_comp_name, tc_comp_ver = tc_comp_info
                fullver = self.det_full_version(ec)
                paths.append(os.path.join(MPI, tc_comp_name, tc_comp_ver, ec['name'], fullver))

        return paths
