# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# Copyright 2009-2023 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/easybuilders/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
EasyBuild support for SuiteSparse, implemented as an easyblock

@author: Stijn De Weirdt (Ghent University)
@author: Dries Verdegem (Ghent University)
@author: Kenneth Hoste (Ghent University)
@author: Pieter De Baets (Ghent University)
@author: Jens Timmerman (Ghent University)
@author: Damian Alvarez (Forschungszentrum Juelich GmbH)
"""
import fileinput
import re
import os
import sys
from distutils.version import LooseVersion

from easybuild.easyblocks.generic.configuremake import ConfigureMake
from easybuild.tools.build_log import EasyBuildError
from easybuild.tools.filetools import mkdir, write_file
from easybuild.tools.modules import get_software_root
from easybuild.tools.modules import get_software_libdir
from easybuild.tools.systemtools import get_shared_lib_ext


class EB_SuiteSparse(ConfigureMake):
    """Support for building SuiteSparse."""

    def __init__(self, *args, **kwargs):
        """Custom constructor for SuiteSparse easyblock, initialize custom class parameters."""
        super(EB_SuiteSparse, self).__init__(*args, **kwargs)
        self.config_name = 'UNKNOWN'

    def configure_step(self):
        """Configure build by patching UFconfig.mk or SuiteSparse_config.mk."""

        if LooseVersion(self.version) < LooseVersion('4.0'):
            self.config_name = 'UFconfig'
        elif LooseVersion(self.version) < LooseVersion('6.0.0'):
            self.config_name = 'SuiteSparse_config'
        else:
            # config file is removed after v6.0.0
            self.config_name = ''

        cfgvars = {
            'CC': os.getenv('CC'),
            'CFLAGS': os.getenv('CFLAGS'),
            'CXX': os.getenv('CXX'),
            'F77': os.getenv('F77'),
            'F77FLAGS': os.getenv('F77FLAGS'),
            'BLAS': os.getenv('LIBBLAS_MT'),
            'LAPACK': os.getenv('LIBLAPACK_MT'),
        }

        # Get CUDA and set it up appropriately
        cuda = get_software_root('CUDA')
        if cuda:
            cuda_cc_space_sep = self.cfg.get_cuda_cc_template_value('cuda_cc_space_sep').replace('.', '').split()
            nvcc_gencode = ' '.join(['-gencode=arch=compute_' + x + ',code=sm_' + x for x in cuda_cc_space_sep])
            cfgvars.update({
                'NVCCFLAGS': ' '.join(['-Xcompiler', '-fPIC', '-O3', nvcc_gencode]),
            })

        # Get METIS or ParMETIS settings
        metis = get_software_root('METIS')
        parmetis = get_software_root('ParMETIS')
        if parmetis or metis:
            if parmetis:
                metis_name = 'ParMETIS'
            else:
                metis_name = 'METIS'
            metis_path = get_software_root(metis_name)
            metis_include = os.path.join(metis_path, 'include')
            metis_libs = os.path.join(metis_path, get_software_libdir(metis_name), 'libmetis.a')

        else:
            self.log.info("Use METIS built in SuiteSparse")
            # raise EasyBuildError("Neither METIS or ParMETIS module loaded.")

        # config file can catch environment variables after v4.5.0
        if LooseVersion(self.version) < LooseVersion('4.5.0'):
            cfgvars.update({
                'INSTALL_LIB': os.path.join(self.installdir, 'lib'),
                'INSTALL_INCLUDE': os.path.join(self.installdir, 'include'),
            })
            if parmetis or metis:
                cfgvars.update({
                    'METIS_PATH': metis_path,
                    'METIS': metis_libs,
                })

            # patch file
            fp = os.path.join(self.cfg['start_dir'], self.config_name, '%s.mk' % self.config_name)

            try:
                for line in fileinput.input(fp, inplace=1, backup='.orig'):
                    for (var, val) in list(cfgvars.items()):
                        # Let's overwrite NVCCFLAGS at the end, since the line breaks and
                        # the fact that it appears multiple times makes it tricky to handle it properly
                        # path variables are also moved to the end
                        if var not in ['NVCCFLAGS', 'INSTALL_LIB', 'INSTALL_INCLUDE', 'METIS_PATH']:
                            orig_line = line
                            # for variables in cfgvars, substiture lines assignment
                            # in the file, whatever they are, by assignments to the
                            # values in cfgvars
                            line = re.sub(r"^\s*(%s\s*=\s*).*\n$" % var,
                                          r"\1 %s # patched by EasyBuild\n" % val,
                                          line)
                            if line != orig_line:
                                cfgvars.pop(var)
                    sys.stdout.write(line)
            except IOError as err:
                raise EasyBuildError("Failed to patch %s in: %s", fp, err)

            # add remaining entries at the end
            if cfgvars:
                cfgtxt = '# lines below added automatically by EasyBuild\n'
                cfgtxt += '\n'.join(["%s = %s" % (var, val) for (var, val) in cfgvars.items()])
                write_file(fp, cfgtxt, append=True)

        elif LooseVersion(self.version) < LooseVersion('6.0.0'):
            # avoid that (system) Intel compilers are always considered
            self.cfg.update('prebuildopts', 'AUTOCC=no')

            # Set BLAS and LAPACK libraries as specified in SuiteSparse README.txt
            self.cfg.update('buildopts', 'BLAS="%s"' % cfgvars.get('BLAS'))
            self.cfg.update('buildopts', 'LAPACK="%s"' % cfgvars.get('LAPACK'))

            self.cfg.update('installopts', 'INSTALL="%s"' % self.installdir)
            self.cfg.update('installopts', 'BLAS="%s"' % cfgvars.get('BLAS'))
            self.cfg.update('installopts', 'LAPACK="%s"' % cfgvars.get('LAPACK'))

            if LooseVersion(self.version) >= LooseVersion('5.1.2'):
                # graphblas exists, needs cmake
                # v5.0.0 until v5.1.2 has no CMAKE_OPTIONS to set
                # probably need patch
                self.cfg.update('preinstallopts', 'CMAKE_OPTIONS="-DCMAKE_INSTALL_PREFIX=%s"' % self.installdir)

            # set METIS library
            if parmetis or metis:
                if LooseVersion(self.version) == LooseVersion('4.5.0'):
                    self.cfg.update('buildopts', 'METIS_PATH="%s"' % metis_path)
                    self.cfg.update('installopts', 'METIS_PATH="%s"' % metis_path)
                else:
                    self.cfg.update('buildopts', 'MY_METIS_LIB="%s"' % metis_libs)
                    self.cfg.update('buildopts', 'MY_METIS_INC="%s"' % metis_include)
                    self.cfg.update('installopts', 'MY_METIS_LIB="%s"' % metis_libs)
                    self.cfg.update('installopts', 'MY_METIS_INC="%s"' % metis_include)

        else:
            # after v6.0.0, no option for metis, its own metis is used anyway
            # nothing to do here, set the CMAKE_OPTIONS in easyconfigs
            pass

    def install_step(self):
        """Install by copying the contents of the builddir to the installdir (preserving permissions)"""

        if LooseVersion(self.version) < LooseVersion('4.5.0'):
            mkdir(os.path.join(self.installdir, 'lib'))
            mkdir(os.path.join(self.installdir, 'include'))

        super(EB_SuiteSparse, self).install_step()

    def sanity_check_step(self):
        """Custom sanity check for SuiteSparse."""

        # Make sure that SuiteSparse did NOT compile its own Metis
        if os.path.exists(os.path.join(self.installdir, 'lib', 'libmetis.%s' % get_shared_lib_ext())):
            raise EasyBuildError("SuiteSparse has compiled its own Metis. This will conflict with the Metis build."
                                 " The SuiteSparse EasyBlock need to be updated!")

        shlib_ext = get_shared_lib_ext()
        libnames = ['AMD', 'BTF', 'CAMD', 'CCOLAMD', 'CHOLMOD', 'COLAMD', 'CXSparse', 'KLU',
                    'LDL', 'RBio', 'SPQR', 'UMFPACK']
        if LooseVersion(self.version) < LooseVersion('4.5'):
            libs = [os.path.join('lib', 'lib%s.a' % x.lower()) for x in libnames]
        else:
            libs = [os.path.join('lib', 'lib%s.%s' % (x.lower(), shlib_ext)) for x in libnames]

        custom_paths = {
            'files': libs,
            'dirs': [],
        }

        super(EB_SuiteSparse, self).sanity_check_step(custom_paths=custom_paths)
