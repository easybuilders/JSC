# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
##
# Copyright 2009-2018 Ghent University
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
EasyBuild support for building and installing netpbm, implemented as an easyblock

@author: Damian Alvarez (Forschungszentrum Juelich GmbH)
"""


import fileinput,os,re,stat,sys
from easybuild.easyblocks.generic.configuremake import ConfigureMake
from easybuild.tools.build_log import EasyBuildError
from easybuild.tools.filetools import adjust_permissions, copy, copy_file, mkdir, move_file, rmtree2, symlink
from easybuild.tools.modules import get_software_root
from easybuild.tools.run import run_cmd

class EB_Netpbm(ConfigureMake):
    """Support for building/installing netpbm."""

    def configure_step(self):
        """Configure netpbm build."""

        deps = ['libjpeg-turbo', 'LibTIFF', 'libpng', 'zlib', 'X11', 'libxml2', 'flex']

        for name in deps:
            if not get_software_root(name):
                raise EasyBuildError("%s module not loaded?", name)

        fn = "config.mk"

        copy_file("config.mk.in", fn)

        for line in fileinput.input(fn, inplace=1, backup='.orig'):

            line = re.sub(r"^BUILD_FIASCO\s*=.*", "BUILD_FIASCO = N", line)
            line = re.sub(r"^CC\s*=.*", "CC = %s" % os.getenv("CC"), line)
            line = re.sub(r"^CFLAGS_FOR_BUILD\s*=.*", "CFLAGS_FOR_BUILD = %s" % os.getenv("CFLAGS"), line)
            line = re.sub(r"^LDFLAGS_FOR_BUILD\s*=.*", "LDFLAGS_FOR_BUILD = %s" % os.getenv("LDFLAGS"), line)
            line = re.sub(r"^CFLAGS_SHLIB\s*=.*", "CFLAGS_SHLIB = -fPIC", line)
            line = re.sub(r"^TIFFLIB\s*=.*", "TIFFLIB = -ltiff", line)
            line = re.sub(r"^TIFFHDR_DIR\s*=.*", "TIFFHDR_DIR = %s/include" % get_software_root("LibTIFF"), line)
            line = re.sub(r"^JPEGLIB\s*=.*", "JPEGLIB = -ljpeg", line)
            line = re.sub(r"^JPEGHDR_DIR\s*=.*", "JPEGHDR_DIR = %s/include" % get_software_root("libjpeg-turbo"), line)
            line = re.sub(r"^PNGLIB\s*=.*", "PNGLIB = -lpng", line)
            line = re.sub(r"^PNGHDR_DIR\s*=.*", "PNGHDR_DIR = %s/include" % get_software_root("libpng"), line)
            line = re.sub(r"^ZLIB\s*=.*", "ZLIB = -lz", line)
            line = re.sub(r"^ZHDR_DIR\s*=.*", "ZHDR_DIR = %s/include" % get_software_root("zlib"), line)
            line = re.sub(r"^JASPERLIB\s*=.*", "JASPERLIB = -ljasper", line)
            line = re.sub(r"^JASPERHDR_DIR\s*=.*", "JASPERHDR_DIR = %s/include" % get_software_root("JasPer"), line)
            line = re.sub(r"^X11LIB\s*=.*", "X11LIB = -lX11", line)
            line = re.sub(r"^X11HDR_DIR\s*=.*", "X11HDR_DIR = %s/include" % get_software_root("X11"), line)
            line = re.sub(r"^OMIT_NETWORK\s*=.*", "OMIT_NETWORK = y", line)

            sys.stdout.write(line)

    def install_step(self):
        """Custom install step for netpbm."""
        # Preinstallation to a tmp directory. Can't install directly to installdir because the make command fails if the
        # directory already exists
        cmd = "make package pkgdir=%s/pkg" % self.builddir
        (out, _) = run_cmd(cmd, log_all=True, simple=False)

        # Move things to installdir
        copy(["%s/pkg/%s" % (self.builddir, x) for x in os.listdir("%s/pkg/" % self.builddir)], self.installdir)

        # Need to do manually the last bits of the installation
        configs = [
            ("%s/config_template" % self.installdir, "%s/bin/netpbm-config" % self.installdir),
            ("%s/pkgconfig_template" % self.installdir, "%s/lib/pkgconfig/netpbm.pc" % self.installdir)
        ]

        mkdir("%s/lib/pkgconfig" % self.installdir)
        for template, config_file in configs:
            move_file(template, config_file)
            for line in fileinput.input(config_file, inplace=1, backup='.orig'):
                if re.match(r"^@", line):
                    continue
                else:
                    line = re.sub(r'@VERSION@', 'Netpbm %s' % self.version, line)
                    line = re.sub(r'@DATADIR@', '%s/lib' % self.installdir, line)
                    line = re.sub(r'@LINKDIR@', '%s/lib' % self.installdir, line)
                    line = re.sub(r'@INCLUDEDIR@', '%s/include' % self.installdir, line)
                    line = re.sub(r'@BINDIR@', '%s/bin' % self.installdir, line)

                sys.stdout.write(line)

        adjust_permissions("%s/bin/netpbm-config" % self.installdir, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        move_file("%s/link/libnetpbm.a" % self.installdir, "%s/lib/libnetpbm.a" % self.installdir)
        symlink("%s/lib/libnetpbm.so.11" % self.installdir, "%s/lib/libnetpbm.so" % self.installdir)
        for f in os.listdir("%s/misc/" % self.installdir):
            move_file("%s/misc/%s" % (self.installdir, f), "%s/lib/%s" % (self.installdir, f))
        rmtree2("%s/misc/" % self.installdir)
        rmtree2("%s/link/" % self.installdir)

        headers = os.listdir("%s/include/netpbm" % self.installdir)
        for header in headers:
            symlink("%s/include/netpbm/%s" % (self.installdir, header), "%s/include/%s" % (self.installdir, header))

        return out

    def sanity_check_step(self):
        """Custom sanity check for netpbm."""

        custom_paths = {
                        'files': ["bin/netpbm-config", "lib/libnetpbm.so" ],
                        'dirs': [],
                       }

        super(ConfigureMake, self).sanity_check_step(custom_paths=custom_paths)
