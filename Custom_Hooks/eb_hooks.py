# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
import os
import re
import subprocess

from easybuild.tools.run import run_cmd
from easybuild.tools.config import build_option
from easybuild.tools.config import install_path
from easybuild.tools.build_log import EasyBuildError, print_msg, print_warning
from easybuild.tools.toolchain.toolchain import SYSTEM_TOOLCHAIN_NAME
from easybuild.toolchains.compiler.systemcompiler import TC_CONSTANT_SYSTEM

SUPPORTED_COMPILERS = ["GCC", "iccifort", "intel-compilers", "NVHPC", "PGI"]
SUPPORTED_MPIS = ["impi", "psmpi", "OpenMPI", "MVAPICH2"]
# Maintain toplevel list for easy use of --try-toolchain
SUPPORTED_TOPLEVEL_TOOLCHAIN_FAMILIES = [
    "intel",
    "intel-para",
    "iomkl",
    "gpsmkl",
    "gomkl",
    "npsmkl",
    "nvomkl",
    "pmvmklc",
    "gmvmklc",
]
SUPPORTED_MPI_TOOLCHAIN_FAMILIES = [
    "iimpi",
    "ipsmpi",
    "iompi",
    "gpsmpi",
    "gompi",
    "npsmpic",
    "nvompic",
    "gmvapich2c",
    "pmvapich2c",
]
# Could potentially make a dictionary of names and supported versions here but that is
# probably overkill
SUPPORTED_TOOLCHAIN_FAMILIES = (
    SUPPORTED_COMPILERS
    + ["gcccoremkl"]
    + ["GCCcore"]
    + SUPPORTED_MPI_TOOLCHAIN_FAMILIES
    + SUPPORTED_TOPLEVEL_TOOLCHAIN_FAMILIES
)
VETOED_INSTALLATIONS = {
        'juwelsbooster': ['impi'],
        'juwels': [''],
        'jurecadc': [''],
        'jurecabooster': ['OpenMPI', 'CUDA', 'nvidia-driver', 'UCX', 'NVHPC'],
        'jusuf': ['impi'],
        'hdfml': [''],
        'deep': [''],
        'hdfcloud': [''],
}

# Also maintain a list of CUDA enabled compilers
CUDA_ENABLED_TOOLCHAINS = ["pmvmklc", "gmvmklc", "gmvapich2c", "pmvapich2c"]
# Use this for a heuristic to see if the easyconfig comes from the Golden Repo
GOLDEN_REPO = "Golden_Repo"

# Some modules should use modaltsoftname by default
REQUIRE_MODALTSOFTNAME = {
    "impi": "IntelMPI",
    "psmpi": "ParaStationMPI",
    "iccifort": "Intel",
    "intel-compilers": "Intel",
}

def installation_vetoer(ec):
    "Check whether this package is NOT supposed to be installed in this system, and abort if necessary"
    name = ec['name']
    system_name = os.getenv('LMOD_SYSTEM_NAME')
    if system_name is None:
        with open('/etc/FZJ/systemname') as sn: system_name = sn.read()
    if name in VETOED_INSTALLATIONS[system_name]:
        print_warning(
                "\nYou are attempting to install software that should not be installed in this system.\n"
                "Please double check the list of packages that you are attempting to install. The following\n"
                f"packages can't be installed in {system_name}:\n"
            )
        for package in VETOED_INSTALLATIONS[system_name]:
            print_msg(f"- {package}", stderr=True)
        exit(1)

def get_user_info():
    # Query jutil to extract the contact information
    if os.getenv('CI') is None:
        jutil = subprocess.Popen([os.getenv('JUMO_USRCMD_EXEC'), 'person', 'show'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = jutil.communicate()
        if not stderr:
            return stdout.decode('utf-8').splitlines()[-1]
        else:
            print_warning(f'Could not query jutil: {stderr}')
            exit(1)
    else:
        return 'CI user <ci_user@fz-juelich.de>'

def inject_site_contact(ec, site_contacts):
    key = "site_contacts"
    value = site_contacts
    ec_dict = ec.asdict()

    if key in ec_dict:
        if ec_dict[key] is not None:
            # Check current values if it is a list
            if isinstance(ec_dict[key], list):
                for contact in ec_dict[key]:
                    email = re.search(r'[\w\.-]+@[\w\.-]+', site_contacts).group(0)
                    # Already in contact
                    if email in contact:
                        break
                # We looped to the end and did not find the contact in this list
                else:
                    # Do not add the generic one if there are other specific contacts
                    if 'sc@fz-juelich.de' not in site_contacts or len(ec_dict[key]) == 0:
                        ec.log.info("[parse hook] Injecting contact %s", value)
                        ec[key].append(site_contacts)
            # Check current values if it is a string
            else:
                email = re.search(r'[\w\.-]+@[\w\.-]+', site_contacts).group(0)
                # Do not add the generic one if there are other specific contacts
                if email not in ec_dict[key] and 'sc@fz-juelich.de' not in site_contacts:
                    ec.log.info("[parse hook] Injecting contact %s", value)
                    ec[key] = [ec_dict[key], site_contacts]
        else:
            ec.log.info("[parse hook] Injecting contact %s", value)
            ec[key] = value
    return ec

def parse_hook(ec, *args, **kwargs):
    """Custom parse hook to manage installations intended for JSC systems."""

    # First of all check if this should be installed
    installation_vetoer(ec)

    ec_dict = ec.asdict()
    # Compilers are are a family (in the Lmod sense)
    if ec.name in SUPPORTED_COMPILERS:
        key = "modluafooter"
        value = 'family("compiler")'
        if key in ec_dict:
            if not value in ec_dict[key]:
                ec[key] = "\n".join([ec[key], value])
        else:
            ec[key] = value
        ec.log.info("[parse hook] Injecting Lmod compiler family")
        # Supported compilers should also be recursively unloaded
        key = "recursive_module_unload"
        if not key in ec_dict or ec_dict[key] is None:
            ec[key] = True
            ec.log.info(
                "[parse hook] Injecting recursive module unloading for supported compiler"
            )

    # Update the dict
    ec_dict = ec.asdict()
    # MPIs are a family (in the Lmod sense) and require to load mpi-settings
    if ec.name in SUPPORTED_MPIS:
        key = "modluafooter"
        value = '''
if not ( isloaded("mpi-settings") ) then
    load("mpi-settings")
end
family("mpi")
        '''
        if key in ec_dict:
            if not value in ec_dict[key]:
                ec[key] = "\n".join([ec[key], value])
        else:
            ec[key] = value
        ec.log.info("[parse hook] Injecting Lmod mpi family and mpi-settings loading")

    # Check if we need to use 'modaltsoftname'
    if ec.name in REQUIRE_MODALTSOFTNAME:
        key = "modaltsoftname"
        if not key in ec_dict or ec_dict[key] is None:
            ec[key] = REQUIRE_MODALTSOFTNAME[ec.name]
            ec.log.info(
                "[parse hook] Injecting modaltsoftname '%s' for '%s'",
                key,
                REQUIRE_MODALTSOFTNAME[ec.name],
            )

    # Check if the module should be installed as hidden
    hidden_pkgs = os.getenv('EASYBUILD_HIDE_DEPS', '').split(',')
    if ec.name in hidden_pkgs:
        key = "hidden"
        if not key in ec_dict or ec_dict[key] is False:
            ec[key] = True
            ec.log.info(
                "[parse hook] Hiding software found in $EASYBUILD_HIDE_DEPS: %s",
                ec.name,
            )

    # Update the dict
    ec_dict = ec.asdict()
    # Check if CUDA is in the dependencies, if so add the GPU Lmod tag
    if (
        "CUDA" in [dep[0] for dep in iter(ec_dict["dependencies"])]
        or ec_dict["toolchain"]["name"] in CUDA_ENABLED_TOOLCHAINS
    ):
        key = "modluafooter"
        value = 'add_property("arch","gpu")'
        if key in ec_dict:
            if not value in ec_dict[key]:
                ec[key] = "\n".join([ec_dict[key], value])
        else:
            ec[key] = value
        ec.log.info("[parse hook] Injecting gpu as Lmod arch property")

    # Update the dict
    ec_dict = ec.asdict()
    # Check where installations are going to go and add appropriate site contact
    # not sure of a fool-proof way to do this, let's just try a heuristic
    site_contacts = None
    # Non-user installation
    if '/p/software' in install_path().lower() or '/gpfs/software' in install_path().lower():
        if 'swmanage' in os.getenv('USER'):
            site_contacts = 'sc@fz-juelich.de'
        else:
            site_contacts = get_user_info()
        # Inject the user
        ec = inject_site_contact(ec, site_contacts)
    # User installation
    else:
        # Tag the build as a user build
        key = "modluafooter"
        value = 'add_property("build","user")'
        if key in ec_dict:
            if not value in ec_dict[key]:
                ec[key] = "\n".join([ec_dict[key], value])
        else:
            ec[key] = value
        ec.log.info("[parse hook] Injecting user as Lmod build property")
        # Inject the user
        site_contacts = get_user_info()
        ec = inject_site_contact(ec, site_contacts)

    # If we are parsing we are not searching, in this case if the easyconfig is
    # located in the search path, warn that it's dependencies will (most probably)
    # not be resolved
    if build_option("robot"):
        search_paths = build_option("search_paths") or []
        robot_paths = list(set(build_option("robot_path") + build_option("robot")))
        if ec.path:
            ec_dir_path = os.path.dirname(os.path.abspath(ec.path))
        else:
            ec_dir_path = ''
        if any(search_path in ec_dir_path for search_path in search_paths) and not any(
            robot_path in ec_dir_path for robot_path in robot_paths
        ):
            raise EasyBuildError(
                "\nYou are attempting to install an easyconfig distributed with "
                "EasyBuild but are not properly configured to resolve dependencies "
                "for this case. Please add additonal options:\n"
                "  eb --robot=$EASYBUILD_ROBOT:$EBROOTEASYBUILD/easybuild/easyconfigs --try-update-deps ...."
            )

def pre_ready_hook(self, *args, **kwargs):
    "When we are building something, do some checks for bad behaviour"
    ec = self.cfg

    # Grab name, path, toolchain, install path and check if we are installing
    # GCCcore/MPI
    name = ec["name"]
    path_to_ec = os.path.abspath(ec.path)
    toolchain = ec["toolchain"]
    is_gcccore = ec["name"] == "GCCcore"
    is_mpi = ec["moduleclass"] == "mpi" or name in SUPPORTED_MPIS

    # Don't let people use unsupported toolchains (by default)
    override_toolchain_check = os.getenv("JSC_OVERRIDE_TOOLCHAIN_CHECK")
    if not override_toolchain_check:
        toolchain_name = toolchain["name"]
        if not toolchain_name in SUPPORTED_TOOLCHAIN_FAMILIES:
            stage = os.getenv("STAGE", default=None)
            if stage:
                # Clean things up if it is a Devel stage
                stage = stage.replace("Devel-", "")
            else:
                stage = "<TOOLCHAIN_VERSION>"
            print_warning(
                "\nYou are attempting to install software with an unsupported "
                "toolchain (%s), please use additional arguments to map this to a supported"
                " toolchain:\n"
                " eb --try-toolchain=<SUPPORTED_TOOLCHAIN>,%s --try-update-deps ...\n"
                "where <SUPPORTED_TOOLCHAIN> comes from the list %s\n"
                "(if you really know what you are doing, you can override this "
                "behaviour by setting the %s environment variable)\n\n"
                "...exiting",
                toolchain_name,
                stage,
                SUPPORTED_TOPLEVEL_TOOLCHAIN_FAMILIES,
                "JSC_OVERRIDE_TOOLCHAIN_CHECK",
            )
            exit(1)

    # Don't let people install GCCcore since this probably won't work and will lead them
    # to reinstall most of our stack. Don't advertise that this can be overridden, only
    # experts should know that.
    override_gcccore_check = os.getenv("JSC_OVERRIDE_GCCCORE_CHECK")
    if not override_gcccore_check:
        if is_gcccore and not "stages" in install_path().lower():
            print_warning(
                "\nYou are attempting to install GCCcore (%s) into a non-system "
                "location (%s), this won't work as expected without additional effort "
                "and is likely to lead to building a whole stack of dependencies even "
                "for simple software. Please contact sc@fz-juelich.de if you wish to "
                "discuss this further.\n\n"
                "...exiting",
                path_to_ec,
                install_path(),
            )
            exit(1)

    # Don't let people install a non-JSC MPI (and don't advertise that this can be
    # overridden, only experts should know that)
    override_mpi_check = os.getenv("JSC_OVERRIDE_MPI_CHECK")
    if not override_mpi_check:
        if is_mpi and GOLDEN_REPO not in path_to_ec:
            print_warning(
                "\nYou are attempting to install a non-system MPI implementation (%s), "
                "this is very likely to lead to severe performance degradation. Please "
                "contact sc@fz-juelich.de if you wish to discuss this further.\n\n"
                "...exiting",
                path_to_ec,
            )
            exit(1)
