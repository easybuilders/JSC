# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
#!/usr/bin/python
# -*- coding: UTF-8 -*-
##
# Copyright 2013 Ghent University
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
EasyBuild support for building and installing AMBER, implemented as an easyblock

@author: Sandipan Mohanty (Jülich Supercomputing Centre)
"""
import os,sys
import re
from distutils.version import LooseVersion
from vsc.utils.missing import any

import easybuild.tools.environment as env
from easybuild.easyblocks.generic.configuremake import ConfigureMake
from easybuild.tools.modules import get_software_root
from easybuild.framework.easyblock import EasyBlock
from easybuild.framework.easyconfig import MANDATORY
from easybuild.framework.easyconfig import CUSTOM
from subprocess import Popen, PIPE, STDOUT, call

class EB_AMBER16(ConfigureMake):
    """Support for building/installing AMBER16."""
    def __init__(self, *args, **kwargs):
        super(EB_AMBER16,self).__init__(*args,**kwargs)
        self.build_in_installdir = True
        env.setvar('AMBERHOME', self.installdir+"/amber16")
        sys.stdout.write("AMBERHOME set to %s/amber16\n"%self.installdir)
        
    @staticmethod
    def extra_options():
        extra_vars = {
            'compilerstr':[None, "Compiler string (gnu/intel/pgi).",MANDATORY],
            'build_mpi_parts':[False, "Build MPI parallelized parts", CUSTOM],
            'build_openmp_parts':[False, "Build OpenMP parts",CUSTOM],
            'build_cuda_parts':[False,"Build CUDA accelerated parts",CUSTOM],
            'amber_python_exe':[None, "Path to the python execuable to be forwarded to AMBER. This could be different from what easybuild is using.", CUSTOM],
            'skip_patches':[False,"Skip downloading and applying patches",CUSTOM],
            'runtest':[False,"Whether to run tests after build",CUSTOM],
        }
        return EasyBlock.extra_options(extra_vars)

#    def extract_step(self):
#        print "Skipping extract step"
#        return None

#    def fetch_step(self):
#        print "Skipping fetch step"
#        return None

    def patch_step(self):
        """Patch AMBER before configuring and thereby avoid interactive configure."""
        if self.cfg['skip_patches'] :
            sys.stdout.write("Skipping over patching step because of explicit easyconfig setting\n")
            return None

        sys.stdout.write("Patching AMBER outside configure script...\n")
        retcd = call(["./update_amber", "--check-updates"])
        if retcd==2 : 
            self.log.info("Updates available. Downloading and applying patches...")
            sys.stdout.write("Updates available. Downloading and applying patches...\n")
            sys.stdout.flush()
            while retcd==2:
                retcd2=call(["./update_amber","--update"])
                if retcd2!=0:
                    self.log.error("Automatic patching failed! Check the errors before re-configuring")

                retcd= call(["./update_amber", "--check-updates"])
        elif retcd==1 : 
            self.log.info("Failed to check for updates")

        return super(EB_AMBER16,self).patch_step()

    def configure_step(self):
        """AMBER uses multiple passes through configure. They are absorbed into the build step."""
        print "Empty configure step from EB_AMBER16 easyblock"
        return None

    def build_step(self):
        compstr = self.cfg.get('compilerstr')
        configopts = self.cfg.get('configopts')
        preconfigopts = self.cfg.get('preconfigopts')
        pythonexe = self.cfg.get('amber_python_exe')
        pythonopt = "--skip-python"
        if pythonexe and os.path.exists(pythonexe):
            pythonopt = "--with-python %s --python-install local" % pythonexe

        configopts=os.path.expandvars(configopts)
        preconfigopts=os.path.expandvars(preconfigopts)

        print "Building AMBER serial ...\nFirst, let's configure for the serial part...\n"
        print "./configure -noX11 --no-updates ",pythonopt,compstr
        configcmd = ["./configure","-noX11","--no-updates", pythonopt, compstr]
        retcd = call(configcmd)
        if retcd!=0:
            self.log.error("Configure failed for AMBER serial part.")
            raise RuntimeError

        print "Configuring AMBER serial was successful. Setting environment variables ..."
        print "Inserting {instpath}/bin to PATH \nand {instpath}/lib to LD_LIBRARY_PATH".format(instpath=os.environ['AMBERHOME'])
        env.setvar('PATH',"{old}:{instpath}/bin".format(old=os.environ['PATH'],instpath=os.environ['AMBERHOME']))
        env.setvar('LD_LIBRARY_PATH',"{old}:{instpath}/lib".format(old=os.environ['LD_LIBRARY_PATH'],instpath=os.environ['AMBERHOME']))
        print "Executing build steps for AMBER serial..."
        outb0 = super(EB_AMBER16,self).build_step()

        if self.cfg['build_mpi_parts'] :
            print "Building AMBER MPI ...\nRun configure again with -mpi\n"
            print "./configure -noX11 -no-updates -mpi ",pythonopt,compstr
            configcmd = ["./configure","-noX11","--no-updates", "-mpi", pythonopt, compstr]
            retcd = call(configcmd)
            if retcd!=0:
                self.log.error("Configure failed for AMBER MPI part.")
                raise RuntimeError

            print "Configuring AMBER MPI part was successful. "
            print "Executing build steps for AMBER MPI ..."
            outb1 = super(EB_AMBER16,self).build_step()
        
        if self.cfg['build_cuda_parts'] :
            print "Building AMBER CUDA support ...\n"
            tmpcudahome=os.environ.get("EBROOTCUDA")
            if not tmpcudahome:
                self.log.error("Expecting EBROOTCUDA to be set to the CUDA tools directory")
                raise ConfigureCUDAFailure

            print "Setting CUDA_HOME to %(ebcuda)s" % {'ebcuda':tmpcudahome}
            env.setvar('CUDA_HOME',tmpcudahome)
            print "Run configure again with -cuda\n"
            print "./configure -noX11 --no-updates -cuda ",pythonopt,compstr
            configcmd = ["./configure","-noX11","--no-updates", "-cuda", pythonopt, compstr]
            retcd = call(configcmd)
            if retcd!=0:
                self.log.error("Configure failed for AMBER CUDA part.")
                raise RuntimeError

            print "Configuring AMBER CUDA part was successful. "
            print "Executing build steps for AMBER CUDA ..."
            outb1 = super(EB_AMBER16,self).build_step()

            if self.cfg['build_mpi_parts'] :
                print "Building AMBER CUDA support for MPI parallel programs...\n"
                print "Run configure again with -cuda -mpi\n"
                print "./configure -noX11 --no-updates -cuda -mpi",pythonopt,compstr
                configcmd = ["./configure","-noX11","--no-updates", "-cuda", "-mpi", pythonopt, compstr]
                retcd = call(configcmd)
                if retcd!=0:
                    self.log.error("Configure failed for AMBER CUDA+MPI part.")
                    raise RuntimeError

                print "Configuring AMBER CUDA+MPI part was successful. "
                print "Executing build steps for AMBER CUDA+MPI ..."
                outb1 = super(EB_AMBER16,self).build_step()

        sys.stdout.write("Reached the end of the build function\n")


    def test_step(self):
        if not self.cfg['runtest'] and not isinstance(self.cfg['runtest'], bool):
            self.cfg['runtest'] = 'test'

        env.setvar('DO_PARALLEL', 'srun -n 8')
        env.setvar('PATH',"{old}:{instpath}/bin".format(old=os.environ['PATH'],instpath=os.environ['AMBERHOME']))
        env.setvar('PYTHONPATH',"{old}:{instpath}/lib/python2.7/site-packages".format(old=os.environ['PYTHONPATH'],instpath=os.environ['AMBERHOME']))
        env.setvar('LD_LIBRARY_PATH',"{old}:{instpath}/lib".format(old=os.environ['LD_LIBRARY_PATH'],instpath=os.environ['AMBERHOME']))

        super(EB_AMBER16, self).test_step()

    def sanity_check_step(self):
        """Custom sanity check for AMBER."""
        return None

