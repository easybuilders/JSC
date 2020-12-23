# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# Copyright 2016-2016 Ghent University
# Copyright 2016-2016 Forschungszentrum Juelich
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
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
EasyBuild support for imvapich2c compiler toolchain (includes Intel and MVAPICH2, and CUDA as dependency).

@author: Damian Alvarez (Forschungszentrum Juelich)
"""

from easybuild.toolchains.iccifort import IccIfort
# We pull in MPI and CUDA at once so this maps nicely to HMNS
from easybuild.toolchains.mpi.mvapich2 import Mvapich2
from easybuild.toolchains.compiler.cuda import Cuda

# Order matters here!
class Imvapich2c(IccIfort, Cuda, Mvapich2):
    """Compiler toolchain with Intel and MVAPICH2, with CUDA as dependency."""
    NAME = 'imvapich2c'
    SUBTOOLCHAIN = IccIfort.NAME
