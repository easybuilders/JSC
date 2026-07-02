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
minor adjustments by Jens Henrik Goebbert (JSC) and Frank W. Wagner (JSC)
"""
import os
import socket

from easybuild.easyblocks.generic.bundle import Bundle
from easybuild.tools.config import build_option
from easybuild.tools import systemtools
from .juliapackage import JuliaPackage


class JuliaBundle(Bundle):
    """Install a Julia package as a separate module or as an extension."""

    @staticmethod
    def extra_options(extra_vars=None):
        """Easyconfig parameters specific to bundles of Julia packages."""
        if extra_vars is None:
            extra_vars = {}
        extra_vars = Bundle.extra_options(extra_vars)
        return JuliaPackage.extra_options(extra_vars)

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

    def __init__(self, *args, **kwargs):
        super(JuliaBundle, self).__init__(*args, **kwargs)
        self.cfg['exts_defaultclass'] = 'JuliaPackage'

        # disable templating so we can update exts_default_options
        with self.cfg.disable_templating():

            exts_opts = {}

            julpkg_keys = JuliaPackage.extra_options().keys()
            for key in julpkg_keys:
                if key not in self.cfg['exts_default_options']:
                    exts_opts[key] = self.cfg[key]

            exts_opts['download_dep_fail'] = True
            self.cfg['exts_default_options'].update(exts_opts)

            self.log.info("Detection of downloaded extension dependencies is enabled.")

        self.log.info("exts_default_options: %s", self.cfg['exts_default_options'])

        # depot/load paths
        self.extensions_depot = 'extensions'

        self.admin_load_path = os.path.join(self.extensions_depot, 'environments', f"{self.version}-{self.get_environment_folder()}")

        self.install_depot = 'local/share/julia'

    def sanity_check_step(self):
        """Custom sanity check for Julia."""
        super(JuliaBundle, self).sanity_check_step(
            custom_paths={
                'files': [],
                'dirs': ['extensions'],
            },
            custom_commands=[]
        )

    def make_module_extra(self, *args, **kwargs):
        txt = super(JuliaBundle, self).make_module_extra(*args, **kwargs)

        # Dict of {'varname': (method, value_or_list)} tuples;
        # method is either 'prepend_paths' or 'append_paths'
        path_vars = {
                'JULIA_DEPOT_PATH': ('append_paths', [self.extensions_depot, self.install_depot]),
                'EBJULIA_ADMIN_DEPOT_PATH': ('prepend_paths', self.extensions_depot),
                'EBJULIA_ADMIN_LOAD_PATH': ('prepend_paths', self.admin_load_path),
                'EBJULIA_STD_DEPOT_PATH': ('append_paths', self.install_depot),
        }

        for var, (method_name, val) in path_vars.items():
            method = getattr(self.module_generator, method_name)
            txt += method(var, val)

        return txt
