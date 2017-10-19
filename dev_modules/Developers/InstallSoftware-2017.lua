-- This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)

help([[
This module will load the environment you need to install new software with EasyBuild in a hierarchy.
]])

whatis("Module to set up the environment for development within EasyBuild")

-- Terminal colors
local red = "\027\[01;31m"
local yellow = "\027\[01;33m"
local green = "\027\[01;32m"
local normal = "\027\[0m"

-- Check first if "Stages" has been loaded. If not print a message and assert it with prereq
if mode()=="load" then
    if not isloaded("Stages") then
        LmodMessage(yellow.."You must have a stage loaded to set the build variables... "..normal)
    end
end

prereq("Stages")

-- Set local variables, taken from the environment
local software_root = os.getenv("SOFTWAREROOT")
local stage =  os.getenv("STAGE")
local is_devel = false
if string.find(stage, "Devel") or string.find(stage, "Stage1")  then
    is_devel = true
end
local stage_path = pathJoin(software_root, "Stages", stage)
local common_eb_path = "/path/to/easybuild/custom/files"

local gr_path = pathJoin(common_eb_path, "Golden_Repo", stage)
local sources_path = pathJoin(common_eb_path, "sources")
local custom_easyblocks_path = pathJoin(common_eb_path, "Custom_EasyBlocks", stage)
local custom_toolchains_path = pathJoin(common_eb_path, "Custom_Toolchains", stage)
local custom_mns_path = pathJoin(common_eb_path, "Custom_MNS", stage)

local contact = "some@contact.com"

-- Allow members of the software group to install *just* in the Devel stage
local user = capture("id -u -n")
-- Sanitize input
user = string.gsub(user, "\n", "")

if mode()=="load" then
    if user ~= "authorized_user" then
        if not userInGroup("software") then
            LmodError(yellow.."Sorry but we only allow installations from users in the software group!\n"..
                      "If you would like to be included in that group please contact: "..
                      contact..normal)
        else
            if not (is_devel and (isloaded("Stages/"..stage) or isloaded("Stages/Devel"))) then
                LmodError(yellow.."Sorry but we only allow installations into Devel stages!\n"..
                          "If you would like a working installation moved to production please contact: "..
                          contact..normal)
            end
        end
    end
end

-- Print header
if mode()=="load" then
    LmodMessage(green.."** LOADING DEVELOPER CONFIGURATION **"..normal.."\n"..
                "Preparing the environment for software installation via EasyBuild into stage "..stage.."\n"..
                "\n"..
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
                "    (EASYBUILD_ROBOT)\n")
end

-- EASYBUILD ENVIRONMENT

-- This should be set to only look in the golden repo. We need this here to prepend overlays if needed
setenv("EASYBUILD_ROBOT", gr_path)
setenv("EASYBUILD_ROBOT_PATHS", gr_path)

-- Fail if there are EB related modules loaded
setenv("EASYBUILD_DETECT_LOADED_MODULES", "error")
-- Whitelist GC3Pie and EasyBuild itself
setenv("EASYBUILD_ALLOW_LOADED_MODULES", "GC3Pie,EasyBuild")

-- Set optarch options for easybuild
local architecture = os.getenv("ARCHITECTURE")
if architecture == "KNL" then
    local opt="GCC:march=knl -mtune=knl;Intel:xMIC-AVX512"
    -- Limit the number of cores, to don't go crazy and use 256+ threads
    local maxparallel = "64"
    if mode()=="load" then
        LmodMessage(yellow.."  - Setting EASYBUILD_OPTARCH to "..opt..normal)
        LmodMessage(yellow.."  - Setting EASYBUILD_PARALLEL to "..maxparallel..normal)
    end
    pushenv("EASYBUILD_OPTARCH", opt)
    pushenv("EASYBUILD_PARALLEL", maxparallel)

    -- Prepend the overlay
    local knl_suffix = "_knl"
    prepend_path("EASYBUILD_ROBOT", gr_path..knl_suffix)
    prepend_path("EASYBUILD_ROBOT_PATHS", gr_path..knl_suffix)
elseif architecture == "SandyBridge" then
    local opt="GCC:march=sandybridge -mtune=sandybridge;Intel:xAVX"
    if mode()=="load" then
        LmodMessage(yellow.."   - Setting EASYBUILD_OPTARCH to "..opt..normal)
    end
    pushenv("EASYBUILD_OPTARCH", opt)
else
    if mode()=="load" then
        LmodMessage("  - "..yellow.."No particular architecture loaded. Unsetting EASYBUILD_OPTARCH (if set)\n"..normal)
    end
    unsetenv("EASYBUILD_OPTARCH")
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
setenv("EASYBUILD_BUILDPATH", pathJoin("/dev/shm", user, architecture))

-- We add our custom Toolchains directory, it must be appended so as not to interfere with the EasyBuild installation
setenv("EASYBUILD_INCLUDE_TOOLCHAINS", pathJoin(custom_toolchains_path, "\*.py"))

-- Finally we add our custom EasyBlock directory, it must be appended so as not to interfere with the EasyBuild installation
setenv("EASYBUILD_INCLUDE_EASYBLOCKS", pathJoin(custom_easyblocks_path, "\*.py")..","..
                                       pathJoin(custom_easyblocks_path, "generic", "\*.py"))

-- Store all installed EasyConfigs in a system-unique repository
setenv("EASYBUILD_REPOSITORY", "FileRepository")
setenv("EASYBUILD_REPOSITORYPATH", pathJoin(stage_path, "eb_repo"))

-- Always hide the following dependencies to keep 'module avail' clean
local hidden_deps = "ANTLR,APR,APR-util,AT-SPI2-ATK,AT-SPI2-core,ATK,Autoconf,Automake,adwaita-icon-theme,ant,assimp,"..
"Bison,babl,binutils,byacc,bzip2,"..
"CUSP,Coreutils,cairo,configurable-http-proxy,"..
"DB,DBus,DocBook-XML,Dyninst,dbus-glib,damageproto,"..
"ETSF_IO,Exiv2,eudev,expat,"..
"FFmpeg,FLTK,FTGL,fixesproto,fontsproto,fontconfig,freeglut,freetype,"..
"GCCcore,GDAL,GEGL,GL2PS,GLEW,GLib,GLPK,GPC,GObject-Introspection,GTI,GTK+,GTS,Gdk-Pixbuf,Ghostscript,GraphicsMagick,GtkSourceView,"..
"g2clib,g2lib,gc,gexiv2,gflags,glog,glproto,gperf,guile,grib_api,gsettings-desktop-schemas,gettext,"..
"HarfBuzz,"..
"icc,ifort,inputproto,intltool,itstool,"..
"JUnit,JSON-C,JSON-GLib,JasPer,jhbuild,"..
"kbproto,"..
"LMDB,LZO,LevelDB,LibTIFF,LibUUID,Libint,LittleCMS,"..
"libGLU,libICE,libSM,libX11,libXau,libXaw,libXcursor,libXdamage,libXdmcp,libXext,libXfixes,libXfont,libXft,libXi,"..
"libXinerama,libXmu,libXpm,libXrandr,libXrender,libXt,libXtst,libcerf,libcroco,libctl,libdap,libdrm,libdwarf,libelf,"..
"libepoxy,libevent,libffi,libfontenc,libgd,libgeotiff,libglade,libidn,libjpeg-turbo,libmatheval,libmypaint,libpng,"..
"libpciaccess,libpthread-stubs,libreadline,librsvg,libsndfile,libtool,libunistring,libunwind,libyaml,libxcb,libxkbcommon,libxml2,"..
"libxslt,libyuv,"..
"M4,Mesa,makedepend,motif,msgpack-c,"..
"NASM,NLopt,ncurses,nettle,nodejs,nvenc_sdk,nvidia,"..
"OPARI2,OTF2,"..
"PCRE,PDT,PROJ,Pango,Pmw,PnMPI,PyCairo,PyGObject,Python-Xpra,pixman,pkg-config,pkgconfig,popt,protobuf,pscom,"..
"Qhull,Qt,Qt5,qrupdate,"..
"randrproto,recordproto,renderproto,"..
"S-Lang,SCons,SIP,SQLite,SWIG,Serf,Szip,scrollkeeper,snappy,"..
"Tcl,Tk,texinfo,"..
"UDUNITS,util-linux,"..
"vpx,"..
"wxPropertyGrid,wxWidgets,"..
"XML-Parser,XZ,XKeyboardConfig,"..
"x264,x265,xbitmaps,xcb-proto,xcb-util,xcb-util-image,xcb-util-keysyms,xcb-util-renderutil,xcb-util-wm,xextproto,"..
"xineramaproto,xorg-macros,xprop,xproto,xtrans,"..
"YAXT,Yasm,"..
"zlib"

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
setenv("EASYBUILD_INCLUDE_MODULE_NAMING_SCHEMES", pathJoin(custom_mns_path, "\*.py"))
setenv("EASYBUILD_MODULE_NAMING_SCHEME", "CustomHierarchicalMNS")

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

-- Let's set things up to use the job submission system to install the software
if not isloaded("GC3Pie") then
    if mode()=="load" then
        LmodMessage(green..
                    "** CONFIGURING DIRECT SUBMISSION TO SLURM **\n"..normal..
                    "Configuring EasyBuild to allow submission of builds as jobs to the devel\n"..
                    "partition (using GC3Pie).\n"..
                    "  - "..yellow.."Loading latest GC3Pie module"..normal.."\n"..
                    "  - Submission configured for SLURM (EASYBUILD_JOB_BACKEND_CONFIG)\n"..
                    "  - Telling EasyBuild to use 32 cores and 1 hour time limit\n"..
                    "    (EASYBUILD_JOB_CORES, EASYBUILD_JOB_MAX_WALLTIME)\n"..
                    yellow.."To access this feature you must add the argument --job to your eb command.\n"..normal..
                    "Please note that execution nodes are *not* connected to the internet so\n"..
                    "software that requires internet access will not build on the back-end.")
    end
    load("GC3Pie")
    setenv("EASYBUILD_JOB_BACKEND", "GC3Pie")
    -- The backend are regular nodes. We have to be careful, some packages might need to be compiled on KNL nodes
    setenv("EASYBUILD_JOB_BACKEND_CONFIG", "/path/to/gc3pie.cfg")
    setenv("EASYBUILD_JOB_CORES", "48")
    setenv("EASYBUILD_JOB_MAX_WALLTIME", "1")
end

-- If not loaded, load the default EasyBuild module
if not isloaded("EasyBuild") then
    if mode()=="load" then
        LmodMessage("  - Loading default (typically latest) EasyBuild module")
    end
    load("EasyBuild")
    -- Enable bash completion in bash
    local shell = capture("echo $SHELL | xargs basename")
    -- Sanitize input
    shell = string.gsub(shell, "\n", "")
--    if shell == "bash" then
--        LmodMessage("  - Enabling bash tab completion for EasyBuild")
--        execute{cmd="source minimal_bash_completion.bash", modeA={"load"}}
--        execute{cmd="source optcomplete.bash", modeA={"load"}}
--        execute{cmd="complete -F _optcomplete eb", modeA={"load"}}
--    end
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
