# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# This file is an EasyBuild reciPY as per https://github.com/easybuilders/easybuild
#
# Copyright:: Copyright 2019 Forschungszentrum Juelich GmbH
# Authors::   Damian Alvarez
# License::   MIT/GPL
# $Id$
##
"""
EasyBuild support for NVIDIA libs, implemented as an easyblock

@author: Damian Alvarez (Forschungszentrum Juelich)
"""
import os

from distutils.version import LooseVersion

from easybuild.easyblocks.generic.binary import Binary
from easybuild.framework.easyconfig import CUSTOM
from easybuild.tools.build_log import EasyBuildError
from easybuild.tools.filetools import copy, expand_glob_paths, mkdir
from easybuild.tools.run import run_cmd
from easybuild.tools.systemtools import get_shared_lib_ext


class EB_nvidia_minus_driver(Binary):
    """
    Support for installing NVIDIA libs.
    """
    @staticmethod
    def extra_options():
        """Support for generic 'default' modules with specific real versions"""
        extra_vars = {
            'realversion': [None, "Real version to be used when version = 'default'", CUSTOM],
        }
        return extra_vars

    def extract_step(self):
        """Extract installer to have more control, e.g. options, patching Perl scripts, etc."""

        if self.cfg['realversion']:
            version = self.cfg['realversion']
        else:
            version = self.version

        if LooseVersion(version) < LooseVersion('400.00'):
            run_files_dir = 'run_files'
        else:
            run_files_dir = 'builds'

        # Source comes from the nvidia drivers
        if self.src[0]['name'].lower().startswith("nvidia"):
            execpath = self.src[0]['path']
        # Source comes from the CUDA toolkit
        else:
            # Decompress initial file
            execpath = self.src[0]['path']
            run_cmd("/bin/sh " + execpath +
                    " --noexec --nox11 --target " + self.builddir)
            execpath = os.path.join(
                self.builddir, run_files_dir, 'NVIDIA-Linux-x86_64-%s.run' % version)

        # Decompress file containing libraries
        self.libsdir = os.path.join(self.builddir, "nvidia-libs")
        run_cmd("/bin/sh " + execpath + " -x --target " + self.libsdir)

    def install_step(self):
        "Install NVIDIA libs simply by copying files. We can't use the installer because it requires root privileges."

        # list of libs
        libs = expand_glob_paths([os.path.join(self.libsdir, 'lib*.so*')])
        try:
            libs += expand_glob_paths([os.path.join(self.libsdir, '*.la')])
        except EasyBuildError:
            self.log.info("No *.la files found. Proceeding without them.")
        libs += [os.path.join(self.libsdir, 'nvidia_drv.so')]

        # list of binaries
        binaries = ['nvidia-bug-report.sh',
                    'nvidia-cuda-mps-control',
                    'nvidia-cuda-mps-server',
                    'nvidia-debugdump',
                    'nvidia-settings',
                    'nvidia-smi',
                    'nvidia-xconfig']
        binaries = [os.path.join(self.libsdir, x) for x in binaries]

        # list of manpages
        manpages = ['nvidia-settings.1.gz',
                    'nvidia-cuda-mps-control.1.gz',
                    'nvidia-xconfig.1.gz',
                    'nvidia-smi.1.gz']
        manpages = [os.path.join(self.libsdir, x) for x in manpages]

        copy(libs, os.path.join(self.installdir, 'lib64'))
        copy(binaries, os.path.join(self.installdir, 'bin'))
        copy(manpages, os.path.join(self.installdir, 'man', 'man1'))

    def post_install_step(self):
        """Generate the appropriate symlinks"""

        libdir = os.path.join(self.installdir, 'lib64')

        # Run ldconfig to create missing symlinks (libcuda.so.1, etc)
        run_cmd("/usr/sbin/ldconfig -N %s" % libdir)

        # Create an extra symlink for libcuda.so, otherwise PGI 19.X breaks
        # Create an extra symlink for libnvidia-ml.so, otherwise MVAPICH2 doesn't find it if it doesn't rely on stubs
        missing_links = ['libcuda.so', 'libnvidia-ml.so']
        for missing_link in missing_links:
            run_cmd("ln -s %s/%s.1 %s/%s" %
                    (libdir, missing_link, libdir, missing_link))

        super(EB_nvidia_minus_driver, self).post_install_step()

    def sanity_check_step(self):
        """Custom sanity check for NVIDIA libs."""

        shlib_ext = get_shared_lib_ext()

        chk_libdir = ["lib64"]

        nvlibs = ["cuda"]
        custom_paths = {
            'files': [os.path.join("bin", x) for x in ["nvidia-smi"]] +
            [os.path.join("%s", "lib%s.%s.1") % (x, y, shlib_ext)
             for x in chk_libdir for y in nvlibs],
            'dirs': [''],
        }

        super(EB_nvidia_minus_driver, self).sanity_check_step(
            custom_paths=custom_paths)
