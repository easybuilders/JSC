-- This file is part of JSC's public easybuild repository (https://github.com/easybuilders/jsc)
--
-- This file is managed or was created by Ansible.
--
-- Terminal colors
local red = "\027\z[01;31m"
local yellow = "\027\z[01;33m"
local green = "\027\z[01;32m"
local normal = "\027\z[0m"

-- Get stage currently used
local old_stage = os.getenv("STAGE")
if old_stage == nil then
    old_stage = "current"
end

-- Software root
local software_root = '/p/software/juwels'

-- Set new stage variables
local stage = myModuleVersion()
local stageroot = pathJoin(software_root, "stages")
local pkgroot = pathJoin(stageroot, stage)

-- Export these so we can use them in any derived modules
setenv("STAGE", stage)
setenv("SOFTWAREROOT", software_root)

-- Lmod messaging functions
help([[  This module will reset your module environment for the requested stage ( ]] .. stage .. [[ ) ]])

whatis([[  Module to set up the environment for requested stage ( ]] .. stage .. [[ )]])

if mode() == "load" then
    if string.find(stage, "Devel") or string.find(stage, "Stage1") then
        LmodMessage("\n  "..yellow.."Development stages are meant for testing "..
                   "software before it gets deployed in production.\n"..
                   "  Please do not use it for production runs, the stage is "..
                   "not meant for that and it should\n"..
                   "  be considered unstable"..normal.."\n")
    else
        local default_stage = capture("readlink -f $(dirname "..myFileName()..")/default | xargs basename -s .lua")
        -- Sanitize input
        default_stage = string.gsub(default_stage, "\n", "")
        if stage < default_stage then
            LmodMessage("\n  "..yellow.."This stage is deprecated. Please consider moving to a new stage ("..default_stage.." or newer)"..normal.."\n")
        elseif stage > default_stage then
            LmodMessage("\n  "..yellow.."This stage is in construction. Thanks for being an early adopter! If you are\n"..
                        "  missing some software you'd like to have, please contact support at sc@fz-juelich.de"..normal.."\n")
        end
    end
end

-- Unload GCCcore, binutils and zlib, loaded by StdEnv. The changes in the MODULEPATH trigger the reloading of StdEnv itself
unload("GCCcore", "binutils", "zlib")

-- Let's tidy things up a little and remove everything Stage/UI related
local old_modulepath = os.getenv("MODULEPATH")
-- Sanitize old_modulepath
if old_modulepath == nil then
    old_modulepath = ""
end
for i in string.gmatch(old_modulepath, "([^:]+)") do
    if string.find(i, "/Stages/") or
        string.find(i, "/stages/") or
        string.find(i, "/UI/Compilers") or
        string.find(i, "/UI/Tools") or
        string.find(i, "/UI/Defaults")
        then
        remove_path("MODULEPATH", i)
    end
end

-- Give access to new stage
prepend_path("MODULEPATH", pathJoin(pkgroot, "UI/Compilers"))
prepend_path("MODULEPATH", pathJoin(pkgroot, "UI/Tools"))
prepend_path("MODULEPATH", pathJoin(pkgroot, "UI/Defaults"))

-- Set the modulerc file per stage
prepend_path("LMOD_MODULERCFILE", pathJoin(pkgroot, "lmod/modulerc.lua"))

-- Make the module 'sticky' so it is hard to unload
add_property("lmod", "sticky")
