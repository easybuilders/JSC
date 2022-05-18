-- This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
--
-- This file is managed or was created by Ansible.
--
help([[
This module will load the environment you need to install new software locally with EasyBuild in a local hierarchy.
]])

whatis("Module to set up the environment for user local software installation with EasyBuild")

-- Terminal colors
local red = "\027\z[01;31m"
local yellow = "\027\z[01;33m"
local green = "\027\z[01;32m"
local normal = "\027\z[0m"

-- Some local variables
local easybuild = "EasyBuild"
local stages =  os.getenv("STAGES")
if stages == nil then
    LmodError(yellow.."Can't determine a value for STAGES (which is usually an environment variable)"..normal)
end

-- If not loaded, load the default EasyBuild module
if not isloaded("EasyBuild") then
    if mode()=="load" then
        LmodMessage("  - Loading default (typically latest) EasyBuild module")
    end
    load("EasyBuild")
end
if mode()=="load" then
    -- Enable bash completion in bash
    local shell = capture("echo $SHELL | xargs basename")
    -- Sanitize input
    shell = string.gsub(shell, "\n", "")
    if shell == "bash" then
        LmodMessage("  - Enabling bash tab completion for EasyBuild and EasyConfigs")
        local bash_completion_cmd = "source $EBROOTEASYBUILD/bin/minimal_bash_completion.bash;\nsource $EBROOTEASYBUILD/bin/optcomplete.bash;\n"
        if os.getenv("JSC_EASYCONFIG_AUTOCOMPLETE") then
            LmodMessage("    (You can disable easyconfig autocomplete from robot ")
            LmodMessage("     search path by unsetting JSC_EASYCONFIG_AUTOCOMPLETE)")
            -- Enable EasyBuild optcomplete and EasyConfig autocomplete
            bash_completion_cmd = bash_completion_cmd.."source $EBROOTEASYBUILD/bin/eb_bash_completion.bash;\n"
        else
            LmodMessage("    (You can enable easyconfig autocomplete from robot ")
            LmodMessage("     search path in addition by setting JSC_EASYCONFIG_AUTOCOMPLETE)")
            -- Enable EasyBuild optcomplete autocomplete
            bash_completion_cmd = bash_completion_cmd.."source /p/fastdata/zam/swmanage/EasyBuild/2022/bin/eb_bash_completion_local.bash;\n"
--             bash_completion_cmd = bash_completion_cmd.."source $EBROOTEASYBUILD/bin/eb_bash_completion_local.bash;\n"
        end
        bash_completion_cmd = bash_completion_cmd.."complete -F _eb eb"
        execute{
            cmd=bash_completion_cmd,
            modeA={"load"}
        }
    end
end

-- Verify that this is a system wide EasyBuild since we rely on this below
if mode()=="load" then
    if (not string.find(os.getenv("EBROOTEASYBUILD"), stages)) then
        LmodError(yellow.."Sorry but we rely on using an EasyBuild module coming from the system!\n"..
                  "If you really want to use your own installation, use a system one first, \n"..
                  "load this module, then afterwards replace the EasyBuild module."..normal)
    end
end

-- Check first if "stages" has been loaded. If not find the stage based on the install path of EasyBuild
local stage =  os.getenv("STAGE")
if stage == nil then
    if mode()=="load" then
        LmodMessage(yellow.."Determining system software installation path from EasyBuild module... "..normal)
    end
    stage =  string.match(os.getenv("EBROOTEASYBUILD"), stages .. "/(.-)/software") or ""
    if stage == nil then
        LmodError(yellow.."Can't determine a value for STAGE (which is usually an environment variable)"..normal)
    end
end

-- Mark it as conflictive with the developers module, to don't allow to load both at the same time
conflict("Developers")

-- Configure an alias for the eb command so that modules in JSC tree are found by eb
-- (it searches for them based on the prefix)
local stage_path = pathJoin(stages, stage)
local stage_base_moduledir = pathJoin(stage_path, "modules/all")
local stage_base_moduledir_core = pathJoin(stage_base_moduledir, "Core")
set_alias("eb","MODULEPATH=" .. stage_base_moduledir .. ':' .. stage_base_moduledir_core .. ':$MODULEPATH STAGE=' .. stage .. " eb")

-- Set local variables
local is_devel = false
if string.find(stage, "Devel") then
    is_devel = true
end

-- Set the path for all system EasyBuild extras
local common_eb_path = pathJoin("/p/fastdata/zam", "swmanage/EasyBuild")
-- need to ensure this path is readable (or a sanitised version available)
if mode()=="load" then
    if lfs.attributes(common_eb_path, "mode") ~= "directory" then
        LmodMessage(yellow.."You do not seem to have read access to the system EasyBuild files,\n"..
                    "please contact software_jsc@fz-juelich.de if you are supposed to have\n"..
                    "access to it. Otherwise, please adjust the $EASYBUILD_* environment variables"..normal)
    end
end

-- Read systemname to know which overlay we should prepend (and where our installations should go)
local systemname = capture("cat /etc/FZJ/systemname")
--Sanitize systemname
systemname = string.gsub(systemname, "\n", "")
local lmod_systemname = os.getenv("LMOD_SYSTEM_NAME")

-- To support cross-compilation
if lmod_systemname == "jurecabooster" then
    systemname = lmod_systemname
end

-- Set up exactly where we put our installations
local subdir_user_modules = pathJoin("easybuild", systemname)
local home_eb = pathJoin(os.getenv("HOME"), subdir_user_modules)
local project_eb = nil
local install_eb = home_eb
local home_install_eb = true
if os.getenv("USERINSTALLATIONS") then
    project_eb = pathJoin(os.getenv("USERINSTALLATIONS"), subdir_user_modules)
    if not os.getenv("PREFER_USER") then
        install_eb = project_eb
        home_install_eb = false
        if mode()=="load" then
            LmodMessage(yellow.."\nFound $USERINSTALLATIONS in the environment, using that for installation. To override this and do \n"..
                        "a personal installation set the environment variable PREFER_USER=1 and reload this module.\n"..normal)
        end
    end
end

-- ensure this is a symlink since there is very little room in HOME directories (and give advice if it isn't)
if mode()=="load" and home_install_eb then
    if lfs.symlinkattributes(pathJoin(os.getenv("HOME"),"easybuild"), "mode") ~= "link" then
        LmodError(yellow.."\nPlease configure ~/easybuild to be a symlink to a location with significant data quotas,\n"..
                  "for example with: \n  mkdir -p $PROJECT/$USER/easybuild && ln -s $PROJECT/$USER/easybuild $HOME/easybuild"..normal)

    else
        LmodMessage(yellow.."\nPerforming a personal installation. To do a project wide installation, \n"..
                   "set the $USERINSTALLATIONS environment variable (for example via jutil).\n"..normal)
    end
end

--set up our JSC configuration specifics

local sources_path = pathJoin(common_eb_path, "sources")
local gr_path = pathJoin(common_eb_path, stage, "Golden_Repo")
local overlay_path = pathJoin(common_eb_path, stage, "Overlays")
local custom_easyblocks_path = pathJoin(common_eb_path, stage, "Custom_EasyBlocks")
local custom_toolchains_path = pathJoin(common_eb_path, stage, "Custom_Toolchains")
local custom_mns_path = pathJoin(common_eb_path, stage, "Custom_MNS")
local custom_hooks = pathJoin(common_eb_path, stage, "Custom_Hooks", "eb_hooks.py")

local custom_module_classes = "astro,base,bio,cae,chem,compiler,data,debugger,devel,"..
                               "geo,ide,lang,lib,math,mpi,numlib,perf,phys,quantum,sidecompiler,"..
                               "system,toolchain,tools,vis"

local user = capture("id -u -n")
user = string.gsub(user, "\n", "")

-- Print header
if mode()=="load" then
    LmodMessage(green.."** LOADING USERSPACE DEVELOPER CONFIGURATION **"..normal.."\n\n"..
                "Preparing the environment for software installation via EasyBuild into userspace leveraging stage "..stage.."\n"..
                "\n"..
                "  - Adding our license servers to LM_LICENSE_FILE \n"..
                "  - Giving priority to JSC custom Toolchains (EASYBUILD_INCLUDE_TOOLCHAINS)\n"..
                "  - Giving priority to JSC custom EasyBlocks (EASYBUILD_INCLUDE_EASYBLOCKS)\n"..
                "  - Giving priority to JSC custom easyconfigs (EASYBUILD_ROBOT)\n"..
                "  - Allowing searching of distribution easyconfigs (EASYBUILD_SEARCH_PATHS)\n"..
                "  - To keep module view clean, hiding some dependencies (EASYBUILD_HIDE_DEPS)\n"..
                "  - Using JSC EasyBuild hooks (EASYBUILD_HOOKS)\n"..
                "  - Setting module classes to include side compilers (EASYBUILD_MOODULECLASSES)\n")
end

-- Unload some modules for convenience
unload("binutils")
unload("GCCcore")
unload("StdEnv")
unload("zlib")

-- EASYBUILD ENVIRONMENT

-- This should be set to only look in the golden repo. We need this here to prepend overlays
setenv("EASYBUILD_ROBOT", gr_path)
setenv("EASYBUILD_ROBOT_PATHS", gr_path)

-- Allow people to search for software in the default path (but is not used to resolve dependencies)
default_robot_path = os.getenv("EBROOTEASYBUILD") .. "/" .. "easybuild" .. "/" .. "easyconfigs"
setenv("EASYBUILD_SEARCH_PATHS", default_robot_path)

-- Configure use of our hooks
setenv("EASYBUILD_HOOKS", custom_hooks)

-- Adding sidecompiler to module classes
setenv("EASYBUILD_MODULECLASSES", custom_module_classes)

-- Fail if there are EB related modules loaded
setenv("EASYBUILD_DETECT_LOADED_MODULES", "error")
-- Whitelist EasyBuild itself
setenv("EASYBUILD_ALLOW_LOADED_MODULES", "EasyBuild")

-- Limit the number of threads
local nproc = capture("nproc")
-- Sanitize input
nproc = string.gsub(nproc, "\n", "")
if tonumber(nproc) > 8 then
    -- Limit the number of threads for user space installs
    local maxparallel = "8"
    pushenv("EASYBUILD_PARALLEL", maxparallel)
    if mode()=="load" then
        LmodMessage(yellow.."  - Setting EASYBUILD_PARALLEL to "..maxparallel..normal)
    end
end

-- Set overlay
gr_overlay_path = pathJoin(overlay_path, systemname.."_overlay")
prepend_path("EASYBUILD_ROBOT", gr_overlay_path)
prepend_path("EASYBUILD_ROBOT_PATHS", gr_overlay_path)

-- Set optarch options for easybuild
local optarch = ""
local cuda_compute = ""
-- JURECA booster
if systemname == "jurecabooster" then
    optarch = "GCCcore:march=haswell -mtune=haswell;GCC:march=knl -mtune=knl -ftree-vectorize;Intel:xMIC-AVX512"
-- JUWELS
elseif systemname == "juwels" then
    optarch = "GCCcore:march=haswell -mtune=haswell"
    cuda_compute = "7.0,6.0"
-- JUWELS booster
elseif systemname == "juwelsbooster" then
    optarch = "Intel:march=core-avx2"
    cuda_compute = "8.0"
-- JURECA-DC
elseif systemname == "jurecadc" then
    optarch = "Intel:march=core-avx2"
    cuda_compute = "8.0,7.5"
-- JUSUF
elseif systemname == "jusuf" then
    optarch = "Intel:march=core-avx2"
    cuda_compute = "7.0"
-- HDFML
elseif systemname == "hdfml" then
    optarch = "GCCcore:march=haswell -mtune=haswell"
    cuda_compute = "7.0"
end

-- Default
if optarch == "" then
    if mode()=="load" then
        LmodMessage("  - "..yellow.."No particular architecture loaded. Unsetting EASYBUILD_OPTARCH (if set)\n"..normal)
    end
    unsetenv("EASYBUILD_OPTARCH")
else
    if mode()=="load" then
        LmodMessage(yellow.."  - Setting EASYBUILD_OPTARCH to "..optarch..normal)
    end
    pushenv("EASYBUILD_OPTARCH", optarch)
end

-- Default
if cuda_compute == "" then
    if mode()=="load" then
        LmodMessage("  - "..yellow.."No particular CUDA compute capability. Unsetting EASYBUILD_CUDA_COMPUTE_CAPABILITIES (if set)\n"..normal)
    end
    unsetenv("EASYBUILD_CUDA_COMPUTE_CAPABILITIES")
else
    if mode()=="load" then
        LmodMessage(yellow.."  - Setting EASYBUILD_CUDA_COMPUTE_CAPABILITIES to "..cuda_compute..normal)
    end
    pushenv("EASYBUILD_CUDA_COMPUTE_CAPABILITIES", cuda_compute)
end

-- Add license servers. Done in 3 separate groups to avoid useless servers in the environment
-- We shuffle the servers too to distribute the load. Not that it matters a lot but....
prepend_path("INTEL_LICENSE_FILE", "1702@licsrv11.zam.kfa-juelich.de:".. -- Intel compilers
                                   "1702@licsrv12.zam.kfa-juelich.de:".. -- Intel compilers
                                   "1702@licsrv13.zam.kfa-juelich.de"   -- Intel compilers
            )
prepend_path("PGROUPD_LICENSE_FILE", "1706@licsrv12.zam.kfa-juelich.de:".. -- PGI compilers
                                     "1706@licsrv13.zam.kfa-juelich.de:".. -- PGI compilers
                                     "1706@licsrv11.zam.kfa-juelich.de"   -- PGI compilers
            )
prepend_path("LM_LICENSE_FILE", "1703@licsrv13.zam.kfa-juelich.de:".. -- TotalView debugger
                                "1703@licsrv11.zam.kfa-juelich.de:".. -- TotalView debugger
                                "1703@licsrv12.zam.kfa-juelich.de"    -- TotalView debugger
            )

setenv("EASYBUILD_PREFIX", install_eb)

-- Make sure that people build in a unique space so we avoid stepping on each others toes as much as possible
setenv("EASYBUILD_BUILDPATH", pathJoin("/dev/shm", user, systemname))

-- We add our custom Toolchains directory, it must be appended so as not to interfere with the EasyBuild installation
setenv("EASYBUILD_INCLUDE_TOOLCHAINS", pathJoin(custom_toolchains_path, "\z*.py")..','..pathJoin(custom_toolchains_path, "fft", "\z*.py")..','..pathJoin(custom_toolchains_path, "compiler", "\z*.py"))

-- Finally we add our custom EasyBlock directory, it must be appended so as not to interfere with the EasyBuild installation
setenv("EASYBUILD_INCLUDE_EASYBLOCKS", pathJoin(custom_easyblocks_path, "\z*.py")..","..
                                       pathJoin(custom_easyblocks_path, "generic", "\z*.py"))

-- Store all installed EasyConfigs in a repository
setenv("EASYBUILD_REPOSITORY", "FileRepository")

-- Always hide these dependencies to keep 'module avail' clean
local hidden_deps = ""
if isFile(gr_path.."/hidden_deps.txt") then
    hidden_deps = capture("tr '\n' ',' < "..gr_path.."/hidden_deps.txt")
end

setenv("EASYBUILD_HIDE_DEPS", hidden_deps)
setenv("EASYBUILD_HIDE_TOOLCHAINS", "GCCcore")

-- Managing permissions and expanding robot path:

-- Tell the robot to search in the users installation when looking for missing dependencies
append_path("EASYBUILD_ROBOT", pathJoin(install_eb, "ebfiles_repo"))

if not home_install_eb then
    setenv("EASYBUILD_SET_GID_BIT", "1")
    if mode()=="load" then
        LmodMessage("  - Using shared group installation, therefore expanding dependency searching\n"..
                    "  - To allow collaboration in the development process, "..red.."all installations are\n"..
                    "    group-writable!"..normal.." (EASYBUILD_GROUP_WRITABLE_INSTALLDIR)")
    end
    -- Tell the robot where to also search there when looking for missing dependencies
    append_path("EASYBUILD_ROBOT", pathJoin(stage_path, "eb_repo"))
    setenv("EASYBUILD_GROUP_WRITABLE_INSTALLDIR", "1")
    setenv("EASYBUILD_UMASK", "002")
    -- We need to allow people to clean out an installation
    setenv("EASYBUILD_STICKY_BIT", "0")
else
    -- The default is to have user-only write access to files/dirs
    setenv("EASYBUILD_UMASK", "022")

    setenv("EASYBUILD_STICKY_BIT", "1")
end

-- The following are details, no need to inform the installer.

-- Indicate that we (currently) use Lmod module tool and lua modules
setenv("EASYBUILD_MODULES_TOOL", "Lmod")
setenv("EASYBUILD_MODULE_SYNTAX", "Lua")

-- Finally we tell EasyBuild to build hierarchical modules using our custom scheme
setenv("EASYBUILD_INCLUDE_MODULE_NAMING_SCHEMES", pathJoin(custom_mns_path, "\z*.py"))
setenv("EASYBUILD_MODULE_NAMING_SCHEME", "FlexibleCustomHierarchicalMNS")

-- Used a fixed installation subdir so that we can change naming schemes later if we want
setenv("EASYBUILD_FIXED_INSTALLDIR_NAMING_SCHEME", "1")

-- Let's make sure we are using minimal toolchains and experimental features
setenv("EASYBUILD_EXPERIMENTAL", "1")
-- This forces EB to do a bottom-top dependency resolution
setenv("EASYBUILD_MINIMAL_TOOLCHAINS", "1")
-- This tells EB to check first if there is a module available that matches any of the subtoolchains, and use it. If
-- multiple exist, the picked up one depends on the order of the paths in MODULEPATH (typically, toolchains higher in
-- the hierarchy will have "preference")
setenv("EASYBUILD_USE_EXISTING_MODULES", "1")

-- Filter for test reports
setenv("EASYBUILD_TEST_REPORT_ENV_FILTER", ".*PS1.*|PROMPT.*|.*LICENSE.*|.*PROJECT.*|.*DATA.*|.*FASTDATA.*|.*SCRATCH.*|.*IMESCRATCH.*|.*HOME.*|.*ARCHIVE.*|.*LOGNAME.*|^SSH|USER|HOSTNAME|UID|.*COOKIE.*")

-- configure tracing by default
setenv("EASYBUILD_TRACE", "1")

-- Let's set things up to use the job submission system to install the software
setenv("EASYBUILD_JOB_BACKEND", "Slurm")
-- Would need to set SLURM environment variables to configure job submission
if mode()=="load" then
    LmodMessage("\n"..yellow.."Note: If you wish to submit software builds to slurm with the "..
                "'--job' flag you will need to set environment variables to configure job submission, see"..
                "\nhttps://slurm.schedmd.com/sbatch.html#lbAJ\nfor details.\n"..normal)
end

-- Let's repeat where we're installing if they've chosen one of the soft-linked Stages
if mode()=="load" then
    if is_devel then
        LmodMessage("You are installing software using a development stage, this is a testing area and\n"..
                    "(group writable) collaboration space to create and verify a build.")
    end
end

-- Prepend the toolchain modules to MODULEPATH, so they are found
prepend_path("MODULEPATH", pathJoin(stages, stage, "UI", "Toolchains"))

-- Add tools directory to path
prepend_path("PATH", pathJoin(common_eb_path, stage, 'bin'))

-- Finally, set EB to use python3
setenv("EB_PYTHON", "python3")
