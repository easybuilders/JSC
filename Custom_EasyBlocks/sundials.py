# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
from easybuild.easyblocks.generic.cmakemake import CMakeMake
from easybuild.tools.modules import get_software_root

class EB_SUNDIALS(CMakeMake):     
    """Support for building Sundials."""

    def __init__(self, *args, **kwargs):
        """Custom constructor for SuiteSparse easyblock, initialize custom class parameters."""        
        super(EB_SUNDIALS, self).__init__(*args, **kwargs)

    def configure_step(self):        
        cuda = get_software_root('CUDA')
        if cuda:            
            cuda_cc_space_sep = self.cfg.template_values['cuda_cc_space_sep'].replace('.','').split()            
            _max = max(cuda_cc_space_sep)
            self.cfg['configopts'] += '-DCMAKE_CUDA_ARCHITECTURES=\"%s\"' %_max            
        super(EB_SUNDIALS, self).configure_step()
