# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# Copyright 2009-2019 Ghent University
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
EasyBuild support for building and installing Julia packages, implemented as an easyblock.

@author: Victor Holanda (CSCS)
@author: Samuel Omlin (CSCS)
@author: Jens Henrik Goebbert (JSC)
@author: Frank W. Wagner (JSC)
"""
import os
import socket
import shutil

from easybuild.framework.easyconfig import CUSTOM
from easybuild.easyblocks.generic.packedbinary import PackedBinary
from easybuild.tools import systemtools


class EB_Julia(PackedBinary):
    """Install a Julia package as a separate module or as an extension."""

    @staticmethod
    def extra_options(extra_vars=None):
        extra_vars = {
            'system_name': [None, "Override Julia Project.toml pathname", CUSTOM],
            'arch_name': [None, "Override Julia Project.toml pathname", CUSTOM],
            'toolchain_name': [None, "Override Julia Project.toml pathname", CUSTOM],
        }
        return PackedBinary.extra_options(extra_vars)

    def get_environment_folder(self):
        """Determine environment folder name based on system and architecture."""
        cfg = self.cfg

        system_name = cfg.get('system_name') or socket.gethostname().split('.')[1]

        arch_name = cfg.get('arch_name')
        if arch_name == '':
            return system_name
        if arch_name:
            return f"{system_name}-{arch_name}"

        toolchain_name = cfg.get('toolchain_name')
        if toolchain_name:
            return toolchain_name

        family = systemtools.get_cpu_family()
        arch = systemtools.get_cpu_architecture()
        return f"{system_name}-{family}-{arch}"

    def get_user_depot_path(self):
        """Return path to user depot."""
        return os.path.join('~', '.julia', self.version, self.get_environment_folder())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        env_folder = self.get_environment_folder()
        env_name = f"{self.version}-{env_folder}"

        # Depot paths
        self.user_depots = self.get_user_depot_path()
        self.admin_depots = os.path.join(self.installdir, 'extensions')
        local_share_depot = os.path.join(self.installdir, 'local', 'share', 'julia')
        self.std_depots = ':'.join([local_share_depot, os.path.join(self.installdir, 'share', 'julia')])
        self.julia_depot_path = ':'.join([self.user_depots, self.std_depots])

        # Project and load paths
        self.julia_project = os.path.join(self.user_depots, 'environments', env_name)
        self.user_load_path = f"@:@#.#.#-{env_folder}"
        self.admin_load_path = os.path.join(self.admin_depots, 'environments', env_name)
        self.std_load_path = f"@stdlib"
        self.julia_load_path = ':'.join([self.user_load_path, self.installdir, self.std_load_path])

    def sanity_check_step(self):
        """Custom sanity check for Julia."""
        super().sanity_check_step(
            custom_paths={
                'files': [os.path.join('bin', 'julia'), 'LICENSE.md'],
                'dirs': ['bin', 'include', 'lib', 'share'],
            },
            custom_commands=["julia --version", "julia --eval '1+2'"]
        )

    def install_step(self, *args, **kwargs):
        """Install procedure for Julia."""
        super().install_step(*args, **kwargs)

        startup_script = os.path.join(self.installdir, 'etc', 'julia', 'startup.jl')
        os.makedirs(os.path.dirname(startup_script), exist_ok=True)

        julia_startup = r"""
## Read EB environment variables
function get_env_list(name)
    haskey(ENV, name) ? split(ENV[name], ':') : []
end

ADMIN_LOAD_PATH = get_env_list("EBJULIA_ADMIN_LOAD_PATH")
STD_LOAD_PATH = get_env_list("EBJULIA_STD_LOAD_PATH")
ADMIN_DEPOT_PATH = get_env_list("EBJULIA_ADMIN_DEPOT_PATH")
STD_DEPOT_PATH = get_env_list("EBJULIA_STD_DEPOT_PATH")

## Inject admin paths unless paths are empty or std-only
if !(isempty(LOAD_PATH) || isempty(DEPOT_PATH) || (length(LOAD_PATH) == 1 && LOAD_PATH[1] == "@") ||
      all(entry in STD_LOAD_PATH for entry in LOAD_PATH) ||
      all(entry in STD_DEPOT_PATH for entry in DEPOT_PATH))

    # Update LOAD_PATH
    user_load = [entry for entry in LOAD_PATH if entry ∉ STD_LOAD_PATH]
    std_load = [entry for entry in LOAD_PATH if entry ∈ STD_LOAD_PATH]
    LOAD_PATH = vcat(user_load, ADMIN_LOAD_PATH, std_load)

    # Update DEPOT_PATH
    user_depot = [entry for entry in DEPOT_PATH if entry ∉ STD_DEPOT_PATH]
    std_depot = [entry for entry in DEPOT_PATH if entry ∈ STD_DEPOT_PATH]
    DEPOT_PATH = vcat(user_depot, ADMIN_DEPOT_PATH, std_depot)
end
"""
        with open(startup_script, 'w') as f:
            f.write(julia_startup)

    def post_install_step(self, *args, **kwargs):
        super().post_install_step(*args, **kwargs)

        # Uncomment below line to remove read-only registries if desired
        # shutil.rmtree(os.path.join(self.admin_depots, 'registries'), ignore_errors=True)

    def make_module_extra(self, *args, **kwargs):
        txt = super().make_module_extra(*args, **kwargs)

        env_folder = self.get_environment_folder()
        env_name = f"{self.version}-{env_folder}"
        env_vars = {
            'JULIA_PROJECT': self.julia_project,
            'JULIA_DEPOT_PATH': self.julia_depot_path,
            'EBJULIA_USER_DEPOT_PATH': self.user_depots,
            'EBJULIA_ADMIN_DEPOT_PATH': self.admin_depots,
            'EBJULIA_STD_DEPOT_PATH': self.std_depots,
            'JULIA_LOAD_PATH': self.julia_load_path,
            'EBJULIA_USER_LOAD_PATH': self.user_load_path,
            'EBJULIA_ADMIN_LOAD_PATH': self.admin_load_path,
            'EBJULIA_STD_LOAD_PATH': self.std_load_path,
            'EBJULIA_ENV_NAME': env_name,
        }

        for k, v in env_vars.items():
            txt += self.module_generator.set_environment(k, v)

        return txt
