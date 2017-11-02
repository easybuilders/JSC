# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# Copyright 2017 Ghent University
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
EasyBuild support for building and installing SciPy-Stack, implemented as an easyblock

@author: Damian Alvarez (Forschungszentrum Juelich GmbH)
"""
import os
from distutils.version import LooseVersion

from easybuild.easyblocks.p.python import EB_Python
from easybuild.tools.build_log import EasyBuildError
from easybuild.tools.filetools import symlink
from easybuild.tools.modules import get_software_version
from easybuild.tools.run import run_cmd
from easybuild.tools.systemtools import get_shared_lib_ext

class EB_SciPy_minus_Stack(EB_Python):
    """Support for building/installing SciPy-Stack"""

    def install_step(self):
        """Extend make install to make sure that the 'python' command is present."""
        super(EB_Python, self).install_step()

        python_binary_path = os.path.join(self.installdir, 'bin', 'python')
        if not os.path.isfile(python_binary_path):
            if os.path.isfile(python_binary_path+'2'):
                pyver = '2'
            elif os.path.isfile(python_binary_path+'3'):
                pyver = '3'
            else:
                raise EasyBuildError("Can't find a python binary in %s", os.path.join(self.installdir, 'bin'))
            symlink(python_binary_path + pyver, python_binary_path)

    def sanity_check_step(self):
        """Custom sanity check for SciPy-Stack."""

        pyver = 'python' + '.'.join(self.version.split('.')[:2])
        shlib_ext = get_shared_lib_ext()

        try:
            fake_mod_data = self.load_fake_module()
        except EasyBuildError, err:
            raise EasyBuildError("Loading fake module failed: %s", err)

        abiflags = ''
        if LooseVersion(self.version) >= LooseVersion("3"):
            run_cmd("which python", log_all=True, simple=False)
            cmd = 'python -c "import sysconfig; print(sysconfig.get_config_var(\'abiflags\'));"'
            (abiflags, _) = run_cmd(cmd, log_all=True, simple=False)
            if not abiflags:
                raise EasyBuildError("Failed to determine abiflags: %s", abiflags)
            else:
                abiflags = abiflags.strip()

        custom_paths = {
            'files': [os.path.join('bin', pyver), os.path.join('lib', 'lib' + pyver + abiflags + '.' + shlib_ext)],
            'dirs': [os.path.join('include', pyver + abiflags), os.path.join('lib', pyver)],
        }

        # cleanup
        self.clean_up_fake_module(fake_mod_data)

        custom_commands = [
            "python --version",
            "python -c 'import _ctypes'",  # make sure that foreign function interface (libffi) works
            "python -c 'import _ssl'",  # make sure SSL support is enabled one way or another
            "python -c 'import readline'",  # make sure readline support was built correctly
        ]

        super(EB_Python, self).sanity_check_step(custom_paths=custom_paths, custom_commands=custom_commands)
