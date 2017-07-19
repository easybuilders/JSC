# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# Copyright 2016-2016 Ghent University
# Copyright 2016-2016 Forschungszentrum Juelich
#
# This file is triple-licensed under GPLv2 (see below), MIT, and
# BSD three-clause licenses.
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
EasyBuild support for pmvmklc compiler toolchain (includes PGI, MVAPICH2 and MKL, and CUDA as dependency).

@author: Damian Alvarez (Forschungszentrum Juelich)
"""

from easybuild.toolchains.pmvapich2c import Pmvapich2c
from easybuild.toolchains.fft.intelfftw import IntelFFTW
from easybuild.toolchains.linalg.intelmkl import IntelMKL


class Pmvmklc(Pmvapich2c, IntelMKL, IntelFFTW):
    """Compiler toolchain with PGI, MVAPICH2 and MKL, and CUDA as dependency."""
    NAME = 'pmvmklc'
    SUBTOOLCHAIN = Pmvapich2c.NAME
