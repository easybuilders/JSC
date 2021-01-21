# This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
import grp
import os

from easybuild.tools.run import run_cmd
from easybuild.tools.config import build_option
from easybuild.tools.config import install_path
from easybuild.tools.build_log import EasyBuildError, print_warning
from easybuild.tools.toolchain.toolchain import SYSTEM_TOOLCHAIN_NAME
from easybuild.toolchains.compiler.systemcompiler import TC_CONSTANT_SYSTEM

SUPPORTED_COMPILERS = ["GCC", "iccifort", "PGI", "GCCcore"]
SUPPORTED_MPIS = ["impi", "psmpi", "OpenMPI", "MVAPICH2"]
# Maintain toplevel list for easy use of --try-toolchain
SUPPORTED_TOPLEVEL_TOOLCHAIN_FAMILIES = [
    "intel",
    "intel-para",
    "iomkl",
    "gpsmkl",
    "gomkl",
    "pmvmklc",
    "gmvmklc",
]
# Could potentially make a dictionary of names and supported versions here but that is
# probably overkill
SUPPORTED_TOOLCHAIN_FAMILIES = (
    SUPPORTED_COMPILERS
    + ["gcccoremkl", "gpsmpi", "ipsmpi", "iimpi", "iompi", "gmvapich2c", "pmvapich2c"]
    + SUPPORTED_TOPLEVEL_TOOLCHAIN_FAMILIES
)
# Also maintain a list of CUDA enabled compilers
CUDA_ENABLED_TOOLCHAINS = ["pmvmklc", "gmvmklc", "gmvapich2c", "pmvapich2c"]
# Use this for a heuristic to see if the easyconfig comes from the Golden Repo
GOLDEN_REPO = "Golden_Repo"

# Some modules should use modaltsoftname by default
REQUIRE_MODALTSOFTNAME = {
    "impi": "IntelMPI",
    "psmpi": "ParaStationMPI",
    "iccifort": "Intel",
}


def parse_hook(ec, *args, **kwargs):
    """Custom parse hook to manage installations intended for JSC systems."""

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
    # MPI are are a family (in the Lmod sense)
    if ec.name in SUPPORTED_MPIS:
        key = "modluafooter"
        value = 'family("mpi")'
        if key in ec_dict:
            if not value in ec_dict[key]:
                ec[key] = "\n".join([ec[key], value])
        else:
            ec[key] = value
        ec.log.info("[parse hook] Injecting Lmod mpi family")

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

    # Check where installations are going to go and add appropriate site contact
    # not sure of a fool-proof way to do this, let's just try a heuristic
    site_contacts = None
    if "stages" in install_path().lower():
        users_groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
        if any(group in user_groups for group in ["swmanage", "software"]):
            site_contacts = "sc@fz-juelich.de"
    if site_contacts is None:
        # Inject the user
        site_contacts = os.getenv("USER")
        # Tag the build as a user build
        key = "modluafooter"
        value = 'add_property("build","user")'
        if key in ec_dict:
            if not value in ec_dict[key]:
                ec[key] = "\n".join([ec_dict[key], value])
        else:
            ec[key] = value
        ec.log.info("[parse hook] Injecting user as Lmod build property")
    if site_contacts:
        key = "site_contacts"
        value = site_contacts
        if key in ec_dict:
            if ec_dict[key] is not None and value not in ec_dict[key]:
                value = ",".join([ec_dict[key], value])
        ec[key] = value
        ec.log.info("[parse hook] Injecting contact %s", value)

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


def end_hook(*args, **kwargs):
    # If the user is part of the development group and the installation is systemwide, 
    # rebuild the system cache
    "Refresh Lmod's cache"

    if "stages" in install_path().lower():
        user = os.getenv("USER")
        if user == "swmanage":
            cmd = (
                "/gpfs/software/juwels/configs/update_system_module_cache.sh"
            )  # Need to make this generic
            if os.path.isfile(cmd):
                print("== Refreshing Lmod's cache...")
                run_cmd(cmd, log_all=True)
    else:
        # Otherwise do nothing, no need to build a user cache, it's very unlikely they 
        # will have loads of modules
        pass

