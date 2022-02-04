-- This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
--
-- This file is managed or was created by Ansible.
--
help([[
This module will load the environment you need to install new software with EasyBuild in a hierarchy.
]])

whatis("Module to set up the environment for development within EasyBuild")

-- Terminal colors
local red = "\027\z[01;31m"
local yellow = "\027\z[01;33m"
local green = "\027\z[01;32m"
local normal = "\027\z[0m"

-- Check first if "Stages" has been loaded. If not print a message and assert it with prereq
if mode()=="load" then
    if not isloaded("Stages") then
        LmodMessage(yellow.."You must have a stage loaded to set the build variables... "..normal)
    end
end

prereq("Stages")

-- Mark it as conflictive with user installations, to don't allow to load both at the same time
conflict("UserInstallations")

-- Read systemname to know which overlay we should prepend and where the module path points to
local systemname = capture("cat /etc/FZJ/systemname")
--Sanitize systemname
systemname = string.gsub(systemname, "\n", "")
local lmod_systemname = os.getenv("LMOD_SYSTEM_NAME")

-- To support cross-compilation
if lmod_systemname == "jurecabooster" then
    systemname = lmod_systemname
end

-- Also check that $HOME/easybuild and $PROJECT/easybuild do not exist, so user installations
-- do not interfere with system-wide installations
if mode()=="load" then
    local user_install_error_msg =  " exists! It might contain user installed software that could\n"..
                                    "interfere with the system wide installation. Please remove this directory "..
                                    "(temporarily if necessary, while you\nperform system-wide installations) and retry."
    if isDir(pathJoin(os.getenv("PROJECT") or "PROJECT_NOT_DEFINED", pathJoin("easybuild", systemname))) then
        LmodError(yellow.."$PROJECT/easybuild/"..systemname..user_install_error_msg..normal)
    end
    if isDir(pathJoin(os.getenv("HOME") or "HOME_NOT_DEFINED", pathJoin("easybuild", systemname))) then
        LmodError(yellow.."$HOME/easybuild/"..systemname..user_install_error_msg..normal)
    end
end

-- Set local variables, taken from the environment
local software_root = os.getenv("SOFTWAREROOT")
local stage =  os.getenv("STAGE")
local is_devel = false
if string.find(stage, "Devel") or string.find(stage, "Stage1")  then
    is_devel = true
end
local stage_path = pathJoin(software_root, "stages", stage)
local fastdata = os.getenv("FASTDATA_jsc")
local common_eb_path = pathJoin(fastdata, "swmanage/EasyBuild")

local sources_path = pathJoin(common_eb_path, "sources")
local gr_path = pathJoin(common_eb_path, stage, "Golden_Repo")
local overlay_path = pathJoin(common_eb_path, stage, "Overlays")
local custom_easyblocks_path = pathJoin(common_eb_path, stage, "Custom_EasyBlocks")
local custom_toolchains_path = pathJoin(common_eb_path, stage, "Custom_Toolchains")
local custom_mns_path = pathJoin(common_eb_path, stage, "Custom_MNS")
local custom_hooks = pathJoin(common_eb_path, stage, "Custom_Hooks", "eb_hooks.py")

local contact = "some@contact.com"

local custom_module_classes = "astro,base,bio,cae,chem,compiler,data,debugger,devel,"..
                               "geo,ide,lang,lib,math,mpi,numlib,perf,phys,quantum,sidecompiler,"..
                               "system,toolchain,tools,vis"

-- Allow members of the software group to install *just* in the Devel stage
local user = capture("id -u -n")
-- Sanitize input
user = string.gsub(user, "\n", "")

if mode()=="load" then
    if user ~= "swmanage" then
        if (not userInGroup("swmanage")) then
            LmodError(yellow.."Sorry but we only allow installations from users in the swmanage group!\n"..
                      "If you would like to be included in that group please contact: "..
                      contact..normal)
        else
            if not (is_devel and (isloaded("Stages/"..stage) or isloaded("Stages/Devel"))) then
                LmodMessage(yellow.."Installation directly in production is possible just to certain directories for\n"..
                          "selected users. If you would like to be allowed to install in the production stage\n"..
                          "please contact: "..contact..normal)
            end
        end
    end
end

-- Print header
if mode()=="load" then
    LmodMessage(green.."** LOADING DEVELOPER CONFIGURATION **"..normal.."\n"..
                "Preparing the environment for software installation via EasyBuild into stage "..stage.."\n"..
                "\n"..
                "  - Unloading preloaded modules \n"..
                "  - Adding our license servers to LM_LICENSE_FILE \n"..
                "  - Setting environment variables for group installations\n"..
                "    (EASYBUILD_SET_GID_BIT, EASYBUILD_STICKY_BIT, EASYBUILD_UMASK, EASYBUILD_GROUP_WRITABLE_INSTALLDIR)\n"..
                "  - Setting environment variable for where sources are stored\n"..
                "    (EASYBUILD_SOURCEPATH)\n"..
                "  - Setting environment variable for installation location\n"..
                "    (EASYBUILD_INSTALLPATH)\n"..
                "  - Setting environment variable for build location (EASYBUILD_BUILDPATH)\n"..
                "  - Giving priority to our custom Toolchains (EASYBUILD_INCLUDE_TOOLCHAINS)\n"..
                "  - Giving priority to our custom EasyBlocks (EASYBUILD_INCLUDE_EASYBLOCKS)\n"..
                "  - Storing all installed EasyConfigs in a unique repository\n"..
                "    (EASYBUILD_REPOSITORY, EASYBUILD_REPOSITORYPATH)\n"..
                "  - To keep module view clean, hiding some dependencies (GCCcore is made invisible with modulerc)\n"..
                "    (EASYBUILD_HIDE_DEPS)\n"..
                "  - Setting the robot path just to our golden repository\n"..
                "    (EASYBUILD_ROBOT)\n"..
                "  - Setting the filter to don't include irrelevant environment information in test reports\n"..
                "    (EASYBUILD_TEST_REPORT_ENV_FILTER)\n"..
                "  - Using JSC EasyBuild hooks (EASYBUILD_HOOKS)\n"..
                "  - Setting module classes to include side compilers (EASYBUILD_MOODULECLASSES)\n")
end

-- Unload some modules for convenience
unload("binutils")
unload("GCCcore")
unload("zlib")
unload("StdEnv")

-- EASYBUILD ENVIRONMENT

-- This should be set to only look in the golden repo. We need this here to prepend overlays
setenv("EASYBUILD_ROBOT", gr_path)
setenv("EASYBUILD_ROBOT_PATHS", gr_path)

-- Configure use of our hooks
setenv("EASYBUILD_HOOKS", custom_hooks)

-- Adding sidecompiler to module classes
setenv("EASYBUILD_MODULECLASSES", custom_module_classes)

-- Fail if there are EB related modules loaded
setenv("EASYBUILD_DETECT_LOADED_MODULES", "error")
-- Whitelist GC3Pie and EasyBuild itself
setenv("EASYBUILD_ALLOW_LOADED_MODULES", "GC3Pie,EasyBuild")

-- Limit the number of threads
local nproc = capture("nproc")
-- Sanitize input
nproc = string.gsub(nproc, "\n", "")
if tonumber(nproc) > 64 then
    -- Limit the number of threads, to don't go crazy and use 256+
    local maxparallel = "64"
    pushenv("EASYBUILD_PARALLEL", maxparallel)
    if mode()=="load" then
        LmodMessage("  - "..yellow.."Setting EASYBUILD_PARALLEL to "..maxparallel..normal)
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
        LmodMessage("  - "..yellow.."Setting EASYBUILD_OPTARCH to "..optarch..normal)
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
        LmodMessage("  - "..yellow.."Setting EASYBUILD_CUDA_COMPUTE_CAPABILITIES to "..cuda_compute..normal)
    end
    pushenv("EASYBUILD_CUDA_COMPUTE_CAPABILITIES", cuda_compute)
end

-- Add license servers. Done in 3 separate groups to avoid useless servers in the environment
-- We shuffle the servers too to distribute the load. Not that it matters a lot but....
prepend_path("INTEL_LICENSE_FILE", "port@license1.server.com:".. -- Intel compilers
                                   "port@license2.server.com:".. -- Intel compilers
                                   "port@license3.server.com"   -- Intel compilers
            )
prepend_path("PGROUPD_LICENSE_FILE", "port@license2.server.com:".. -- PGI compilers
                                     "port@license3.server.com:".. -- PGI compilers
                                     "port@license1.server.com"   -- PGI compilers
            )
prepend_path("LM_LICENSE_FILE", "port@license3.server.com:".. -- TotalView debugger
                                "port@license1.server.com:".. -- TotalView debugger
                                "port@license2.server.com"    -- TotalView debugger
            )

-- Set up exactly where we put our installations
-- First: where are the sources stored/downloaded 
setenv("EASYBUILD_SOURCEPATH", sources_path)

-- Second: where are the software and modules stored 
setenv("EASYBUILD_INSTALLPATH", stage_path)

-- Make sure that people build in a unique space so we avoid stepping on each others toes as much as possible
setenv("EASYBUILD_BUILDPATH", pathJoin("/dev/shm", user, systemname))

-- We add our custom Toolchains directory, it must be appended so as not to interfere with the EasyBuild installation
setenv("EASYBUILD_INCLUDE_TOOLCHAINS", pathJoin(custom_toolchains_path, "\z*.py")..','..pathJoin(custom_toolchains_path, "fft", "\z*.py")..','..pathJoin(custom_toolchains_path, "compiler", "\z*.py"))

-- Finally we add our custom EasyBlock directory, it must be appended so as not to interfere with the EasyBuild installation
setenv("EASYBUILD_INCLUDE_EASYBLOCKS", pathJoin(custom_easyblocks_path, "\z*.py")..","..
                                       pathJoin(custom_easyblocks_path, "generic", "\z*.py"))

-- Store all installed EasyConfigs in a system-unique repository
setenv("EASYBUILD_REPOSITORY", "FileRepository")
setenv("EASYBUILD_REPOSITORYPATH", pathJoin(stage_path, "eb_repo"))


-- Always hide these dependencies to keep 'module avail' clean
local hidden_deps = ""
if isFile(gr_path.."/hidden_deps.txt") then
    hidden_deps = capture("tr '\n' ',' < "..gr_path.."/hidden_deps.txt")
end

setenv("EASYBUILD_HIDE_DEPS", hidden_deps)

setenv("EASYBUILD_HIDE_TOOLCHAINS", "GCCcore")

-- Managing permissions and expanding robot path
-- Setting variables to allow for a group install space
setenv("EASYBUILD_SET_GID_BIT", "1")

if is_devel and (isloaded("Stages/"..stage) or isloaded("Stages/Devel")) then
    if mode()=="load" then
        LmodMessage("  - Installing in Devel stage, therefore expanding dependency searching\n"..
                    "  - To allow collaboration in the development process, "..red.."all installations are\n"..
                    "    group-writable!"..normal.." (EASYBUILD_GROUP_WRITABLE_INSTALLDIR)")
    end
    -- Tell the robot where to search there when looking for missing dependencies
    append_path("EASYBUILD_ROBOT", pathJoin(stage_path, "eb_repo"))
    setenv("EASYBUILD_GROUP_WRITABLE_INSTALLDIR", "1")
    setenv("EASYBUILD_UMASK", "002")
    -- We need to allow people to clean out an installation in Devel
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

-- Set the prefix for EasyBuild
setenv("EASYBUILD_PREFIX", stage_path)

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

-- Enable user installations
setenv("EASYBUILD_SUBDIR_USER_MODULES", pathJoin("easybuild", systemname, "modules"))
setenv("EASYBUILD_ENVVARS_USER_MODULES", "PROJECT,HOME")

-- Filter for test reports
setenv("EASYBUILD_TEST_REPORT_ENV_FILTER", ".*PS1.*|PROMPT.*|.*LICENSE.*|.*PROJECT.*|.*DATA.*|.*FASTDATA.*|.*SCRATCH.*|.*IMESCRATCH.*|.*HOME.*|.*ARCHIVE.*|.*LOGNAME.*|^SSH|USER|HOSTNAME|UID|.*COOKIE.*")


-- Set up the hooks to automatically refresh the cache and stop waiting for the cronjob to do it
--if user == "swmanage" then
--    setenv("EASYBUILD_HOOKS", "/gpfs/software/juwels/configs/eb_hooks.py")
--end

-- Let's set things up to use the job submission system to install the software
--if not isloaded("GC3Pie") then
--    if mode()=="load" then
--        LmodMessage(green..
--                    "** CONFIGURING DIRECT SUBMISSION TO SLURM **\n"..normal..
--                    "Configuring EasyBuild to allow submission of builds as jobs to the devel\n"..
--                    "partition (using GC3Pie).\n"..
--                    "  - "..yellow.."Loading latest GC3Pie module"..normal.."\n"..
--                    "  - Submission configured for SLURM (EASYBUILD_JOB_BACKEND_CONFIG)\n"..
--                    "  - Telling EasyBuild to use 32 cores and 1 hour time limit\n"..
--                    "    (EASYBUILD_JOB_CORES, EASYBUILD_JOB_MAX_WALLTIME)\n"..
--                    yellow.."To access this feature you must add the argument --job to your eb command.\n"..normal..
--                    "Please note that execution nodes are *not* connected to the internet so\n"..
--                    "software that requires internet access will not build on the back-end.")
--    end
--    load("GC3Pie")
--    setenv("EASYBUILD_JOB_BACKEND", "GC3Pie")
--    -- The backend are regular nodes. We have to be careful, some packages might need to be compiled on KNL nodes
--    setenv("EASYBUILD_JOB_BACKEND_CONFIG", "/path/to/gc3pie.cfg")
--    setenv("EASYBUILD_JOB_CORES", "48")
--    setenv("EASYBUILD_JOB_MAX_WALLTIME", "1")
--end

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
        LmodMessage("  - Enabling bash tab completion for EasyBuild")
        -- Enable EasyBuild autocomplete
        execute{
            cmd=[[
                source $EBROOTEASYBUILD/bin/minimal_bash_completion.bash;
                source $EBROOTEASYBUILD/bin/optcomplete.bash;
                source $EBROOTEASYBUILD/bin/eb_bash_completion.bash;
                complete -F _eb eb
            ]],
            modeA={"load"}
        }
    end
end

-- Let's repeat where we're installing if they've chosen one of the soft-linked Stages
if mode()=="load" then
    if not is_devel then
        LmodMessage("\n"..red.."Warning! You are installing software into a production stage. This\n"..
                    "should typically only be done (rarely!) for bug fixes and verified builds.\n"..normal)
    else
        LmodMessage("You are installing software in the development stage, this is a testing area and\n"..
                    "(group writable) collaboration space to create and verify a build.")
    end
end

-- Add tools directory to path
prepend_path("PATH", pathJoin(common_eb_path, stage, 'bin'))

-- Finally, set EB to use python3
setenv("EB_PYTHON", "python3")
