# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# Copyright 2009-2015 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/easybuild
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
EasyBuild support for building and installing Tau, implemented as an easyblock

@author Kenneth Hoste (Ghent University)
@author Markus Geimer (Juelich Supercomputing Centre)
@author Bernd Mohr (Juelich Supercomputing Centre)
"""
import os

from easybuild.easyblocks.generic.configuremake import ConfigureMake
from easybuild.framework.easyconfig import CUSTOM
from easybuild.tools import toolchain
from easybuild.tools.build_log import EasyBuildError, print_msg
from easybuild.tools.modules import get_software_libdir, get_software_root, get_software_version
from easybuild.tools.run import run_cmd


KNOWN_BACKENDS = ['scalasca', 'scorep', 'vampirtrace']


class EB_TAU(ConfigureMake):
    """Support for building/installing Tau."""

    @staticmethod
    def extra_options():
        """Custom easyconfig parameters for Tau."""
        backends_helpmsg = "Extra Tau backends to build and install; possible values: %s" % ','.join(KNOWN_BACKENDS)
        extra_vars = {
            'extra_backends': [[], backends_helpmsg, CUSTOM],
            'tau_makefile': ['Makefile.tau-papi-mpi-pdt', "Name of Makefile to use in $TAU_MAKEFILE", CUSTOM],
         }
        return ConfigureMake.extra_options(extra_vars)

    def __init__(self, *args, **kwargs):
        super(EB_TAU, self).__init__(*args, **kwargs)

        out, _ = run_cmd("uname -m", simple=False)
        self.machine = out.strip()
        self.log.info("Using '%s' as machine label", self.machine)

        self.variant_index = 0

    def run_all_steps(self, *args, **kwargs):
        """
        Put configure options in place for the different selected backends of Tau,
        for the MPI, OpenMP and hybrid variants.
        """
        # make sure selected extra backends are known
        unknown_backends = []
        for backend in self.cfg['extra_backends']:
            if backend not in KNOWN_BACKENDS:
                unknown_backends.append(backend)
        if unknown_backends:
            raise EasyBuildError("Encountered unknown backends: %s" % ', '.join(unknown_backends))

        # compiler options
        comp_opts = "-cc=%(cc)s -c++=%(cxx)s -fortran=%(fortran)s"

        # variant-specific options
        openmp_opts = " -opari"
        mpi_opts = " -mpiinc=%(mpi_inc_dir)s -mpilib=%(mpi_lib_dir)s"

        # options for optional packages
        opt_pkgs_opts = " %(opt_pkgs_opts)s"

        # backend option
        backend_opt = " %(backend_opt)s"

        # compose templates
        mpi_tmpl = comp_opts + mpi_opts + opt_pkgs_opts + backend_opt
        openmp_tmpl = comp_opts + openmp_opts + opt_pkgs_opts + backend_opt
        hybrid_tmpl = comp_opts + openmp_opts + mpi_opts + opt_pkgs_opts + backend_opt

        # number of iterations: # backends + 1 (for basic)
        iter_cnt = len(self.cfg['extra_backends']) + 1

        self.cfg['configopts'] = [mpi_tmpl, openmp_tmpl, hybrid_tmpl] * iter_cnt

        # custom prefix option for configure command
        self.cfg['prefix_opt'] = '-prefix='

        # installation command is 'make install clean'
        self.cfg['installopts'] = 'clean'

        return super(EB_TAU, self).run_all_steps(*args, **kwargs)

    def guess_start_dir(self):
        """Guess start directory and inform which backend/variant is being handled next."""
        super(EB_TAU, self).guess_start_dir()

        # inform which backend/variant is being handled next
        backend = (['tau'] + self.cfg['extra_backends'])[self.variant_index // 3]
        variant = ['mpi', 'openmp', 'hybrid'][self.variant_index % 3]
        print_msg("starting with %s backend (%s variant)" % (backend, variant), log=self.log)

    def prepare_step(self):
        """Custom prepare step for Tau: check required dependencies and collect information on them."""
        super(EB_TAU, self).prepare_step()

        # install prefixes for selected backends
        for dep in ['Scalasca', 'Score-P', 'Vampirtrace']:
            root = get_software_root(dep)
            backend_name = dep.lower().replace('-', '')
            if backend_name in self.cfg['extra_backends']:
                if root:
                    setattr(self, backend_name, root)
                else:
                    raise EasyBuildError("%s is listed in extra_backends, but not available as a dependency" % dep)
            elif root:
                raise EasyBuildError("%s included as dependency, but '%s' not in extra_backends" % (dep, backend_name))

        # make sure Scalasca v1.x is used as a dependency (if it's there)
        if hasattr(self, 'scalasca') and get_software_version('Scalasca').split('.')[0] != '1':
            raise EasyBuildError("Scalasca v1.x must be used when scalasca backend is enabled")

        # determine values for compiler flags to use
        known_compilers = {
            toolchain.CLANGGCC: ['clang', 'clang++', 'gfortran'],
            toolchain.GCC: ['gcc', 'g++', 'gfortran'],
            toolchain.INTELCOMP: ['icc', 'icpc', 'intel'],
        }
        comp_fam = self.toolchain.comp_family()
        if comp_fam in known_compilers:
            self.cc, self.cxx, self.fortran = known_compilers[comp_fam]
        else:
            raise EasyBuildError("Compiler family not supported yet: %s" % comp_fam)

        # determine values for MPI flags
        self.mpi_inc_dir, self.mpi_lib_dir = os.getenv('MPI_INC_DIR'), os.getenv('MPI_LIB_DIR')
        if self.mpi_inc_dir is None or self.mpi_lib_dir is None:
            raise EasyBuildError("Failed to determine MPI include/library paths, no MPI available in toolchain?")

        # determine value for optional packages option template
        self.opt_pkgs_opts = ''
        for dep, opt in [('PAPI', 'papi'), ('PDT', 'pdt'), ('binutils', 'bfd')]:
            root = get_software_root(dep)
            if root:
                self.opt_pkgs_opts += ' -%s=%s' % (opt, root)

        # determine list of labels, based on selected (extra) backends, variants and optional packages
        self.variant_labels = []
        backend_labels = ['', '-epilog-scalasca-trace', '-scorep', '-vampirtrace-trace']
        for backend, backend_label in zip(['tau'] + KNOWN_BACKENDS, backend_labels):
            if backend == 'tau' or backend in self.cfg['extra_backends']:

                for pref, suff in [('-mpi', ''), ('', '-openmp-opari'), ('-mpi', '-openmp-opari')]:

                    variant_label = 'tau'

                    if self.cxx != 'g++':
                        variant_label += '-' + self.cxx

                    if get_software_root('PAPI'):
                        variant_label += '-papi'

                    variant_label += pref

                    if get_software_root('PDT'):
                        variant_label += '-pdt'

                    variant_label += suff + backend_label

                    self.variant_labels.append(variant_label)

        # make sure selected default Tau makefile will be available
        avail_makefiles = ['Makefile.' + l for l in self.variant_labels]
        if self.cfg['tau_makefile'] not in avail_makefiles:
            tup = (self.cfg['tau_makefile'], avail_makefiles)
            raise EasyBuildError("Specified tau_makefile %s will not be available (only: %s)" % tup)

        # create install directory and make sure it does not get cleaned up again in the install step;
        # the first configure iteration already puts things in place in the install directory,
        # so that shouldn't get cleaned up afterwards...
        self.log.info("Creating install dir %s before starting configure-build-install iterations", self.installdir)
        self.make_installdir()
        self.cfg['keeppreviousinstall'] = True

    def configure_step(self):
        """Custom configuration procedure for Tau: template configuration options before using them."""

        active_backend = (['tau'] + self.cfg['extra_backends'])[self.variant_index // 3]
        backend_opts = {
            'scalasca': '-scalasca=%s' % getattr(self, 'scalasca', 'NOTDEFINED'),
            'scorep': '-scorep=%s' % getattr(self, 'scorep', 'NOTDEFINED'),
            'tau': '',
            'vampirtrace': '-vampirtrace=%s' % getattr(self, 'vampirtrace', 'NOTDEFINED'),
        }

        self.cfg['configopts'] = self.cfg['configopts'] % {
            'backend_opt': backend_opts[active_backend],
            'cc': self.cc,
            'cxx': self.cxx,
            'fortran': self.fortran,
            'mpi_inc_dir': self.mpi_inc_dir,
            'mpi_lib_dir': self.mpi_lib_dir,
            'opt_pkgs_opts': self.opt_pkgs_opts,
        }

        for key in ['preconfigopts', 'configopts', 'prebuildopts', 'preinstallopts']:
            self.log.debug("%s: %s", key, self.cfg[key])

        super(EB_TAU, self).configure_step()

        self.variant_index += 1

    def build_step(self):
        """No custom build procedure for Tau."""
        pass

    def sanity_check_step(self):
        """Custom sanity check for Tau."""
        custom_paths = {
            'files': [os.path.join(self.machine, 'bin', 'pprof'), os.path.join('include', 'TAU.h'),
                      os.path.join(self.machine, 'lib', 'libTAU.so')] +
                     [os.path.join(self.machine, 'lib', 'lib%s.a' % l) for l in self.variant_labels] +
                     [os.path.join(self.machine, 'lib', 'Makefile.' + l) for l in self.variant_labels],
            'dirs': [],
        }
        super(EB_TAU, self).sanity_check_step(custom_paths=custom_paths)

    def make_module_req_guess(self):
        """Custom guesses for environment variables (PATH, ...) for Tau."""
        guesses = super(EB_TAU, self).make_module_req_guess()
        guesses.update({
            'PATH': [os.path.join(self.machine, 'bin')],
        })
        return guesses

    def make_module_extra(self):
        """Custom extra module file entries for Tau."""
        txt = super(EB_TAU, self).make_module_extra()
        txt += self.module_generator.prepend_paths('TAU_MF_DIR', os.path.join(self.machine, 'lib'))

        tau_makefile = os.path.join(self.installdir, self.machine, 'lib', self.cfg['tau_makefile'])
        txt += self.module_generator.set_environment('TAU_MAKEFILE', tau_makefile)

        return txt
