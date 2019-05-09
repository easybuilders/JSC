# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# Copyright 2017 Forschungszentrum Juelich GmbH
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# Flemish Research Foundation (FWO) (http://www.fwo.be/en)
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
@author: Damian Alvarez (Forschungszentrum Juelich GmbH)
"""

from easybuild.easyblocks.generic.bundle import Bundle

class SystemBundle(Bundle):
    """
    Support for creating a bundle that allows to prepend absolute paths in LD_LIBRARY_PATH
    """

    def make_module_extra(self):
        """Prepend variables allowing absolute paths, and proceed as normal"""

        lines = ['']
        modextrapaths = self.cfg['modextrapaths']

        for (key, value) in self.cfg['modextrapaths'].items():
            if isinstance(value, basestring):
                value = [value]
            elif not isinstance(value, (tuple, list)):
                raise EasyBuildError("modextrapaths dict value %s (type: %s) is not a list or tuple",
                                     value, type(value))
            lines.append(self.module_generator.prepend_paths(key, value, allow_abs=True))

        self.cfg['modextrapaths'] = {}

        txt = super(SystemBundle, self).make_module_extra()
        self.cfg['modextrapaths'] = modextrapaths

        txt += ''.join(lines)

        return txt
