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
            'just_GL_libs': [False, "Install just GL-related libs", CUSTOM],
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
        if not self.cfg['just_GL_libs']:
            libs = expand_glob_paths([os.path.join(self.libsdir, 'lib*.so*')])
            try:
                libs += expand_glob_paths([os.path.join(self.libsdir, '*.la')])
            except EasyBuildError:
                self.log.info("No *.la files found. Proceeding without them.")
            libs += [os.path.join(self.libsdir, 'nvidia_drv.so')]
        else:
            libs = expand_glob_paths([os.path.join(self.libsdir, 'libEGL*.so*')])
            libs += expand_glob_paths([os.path.join(self.libsdir, 'libGL*.so*')])
            libs += expand_glob_paths([os.path.join(self.libsdir, 'libOpenGL.so*')])
            libs += expand_glob_paths([os.path.join(self.libsdir, 'libnvidia-egl*.so*')])
            libs += expand_glob_paths([os.path.join(self.libsdir, 'libnvidia-gl*.so*')])
            libs += expand_glob_paths([os.path.join(self.libsdir, 'libnvidia-rtcore*.so*')])
            libs += expand_glob_paths([os.path.join(self.libsdir, 'libnvidia-tls*.so*')])
            libs += expand_glob_paths([os.path.join(self.libsdir, 'libnvidia-vulkan*.so*')])


        if not self.cfg['just_GL_libs']:
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

            copy(binaries, os.path.join(self.installdir, 'bin'))
            copy(manpages, os.path.join(self.installdir, 'man', 'man1'))

        copy(libs, os.path.join(self.installdir, 'lib64'))

    def post_install_step(self):
        """Generate the appropriate symlinks"""

        libdir = os.path.join(self.installdir, 'lib64')

        # Run ldconfig to create missing symlinks (libcuda.so.1, etc)
        run_cmd("/usr/sbin/ldconfig -N %s" % libdir)

        if not self.cfg['just_GL_libs']:
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

        if not self.cfg['just_GL_libs']:
            nvlibs = ["cuda"]
            binaries = [os.path.join("bin", x) for x in ["nvidia-smi"]]
            libs = [os.path.join("%s", "lib%s.%s.1") % (x, y, shlib_ext)
                    for x in chk_libdir for y in nvlibs]
        else:
            nvlibs_0_suffix = ["EGL_nvidia", "GLX_nvidia", "OpenGL"]
            nvlibs_1_suffix = ["GLESv1_CM_nvidia"]
            nvlibs_2_suffix = ["GLESv2_nvidia"]
            binaries = []
            libs = [os.path.join("%s", "lib%s.%s.0") % (x, y, shlib_ext)
                    for x in chk_libdir for y in nvlibs_0_suffix]
            libs += [os.path.join("%s", "lib%s.%s.1") % (x, y, shlib_ext)
                     for x in chk_libdir for y in nvlibs_1_suffix]
            libs += [os.path.join("%s", "lib%s.%s.2") % (x, y, shlib_ext)
                     for x in chk_libdir for y in nvlibs_2_suffix]

        custom_paths = {
            'files': binaries + libs,
            'dirs': [''],
        }
        super(EB_nvidia_minus_driver, self).sanity_check_step(
            custom_paths=custom_paths)
