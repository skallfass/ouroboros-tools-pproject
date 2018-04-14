#!/bin/bash
export AUTOACTIVATE=1
export AUTOUPDATE=1
export PATH=$conda_folder/bin:$PATH


CYAN='\033[0;94m'
GREEN='\033[1;92m'
RED='\033[1;91m'
COLOR_END='\033[0m'
AS_BOLD='\033[1;37m'


###############################################################################
# Returns customized output of status during project command.
# The output has the following form (with colors):
#     STATUS  STAGE  MESSAGE
# Example:
#     E  UPDATE could not find meta.yaml
# -----------------------------------------------------------------------------
# Arguments:
#   $1: functionname to pass
#   $2: state to print
###############################################################################
function pproject::log(){
    typeset -A _scripts;
    _scripts["A"]="              ${CYAN}AUTOENV${COLOR_END} "
    _scripts["AU"]="           ${CYAN}AUTOUPDATE${COLOR_END} "
    _scripts["none"]="                     "
    typeset -A _script_states;
    _script_states["_"]="  "
    _script_states["E"]=" ${RED}E${COLOR_END}"
    _script_states["info"]=" ${AS_BOLD}"'\u2139'"${COLOR_END}"
    _script_states["F"]=" ${GREEN}"'\u2714'"${COLOR_END}"
    _script_states["x"]=" ${RED}"'\u2718'"${COLOR_END}"
    echo -e ${_script_states["$2"]}${_scripts["$1"]}"$3"
}


###############################################################################
# Checks if the meta.yaml file as defined in variable $META_YAML_PTH exists
# -----------------------------------------------------------------------------
# Globals:
#     $meta_yaml_path: from config-file.
###############################################################################
function pproject::check_if_meta_yaml(){
    if [ -e $meta_yaml_path ]; then
        return 0;
    else
        pproject::log "P" "E" "There is no $meta_yaml_path"
        pproject::log "P" "x"
        return 1;
    fi
}


###############################################################################
# Collect the value of a passed key (searchstring) in the meta.yaml-file and
# returns the result.
# -----------------------------------------------------------------------------
# Arguments:
#     $1: searchstring
# -----------------------------------------------------------------------------
# Globals:
#     $meta_yaml_path
# -----------------------------------------------------------------------------
# Returns:
#     value of the passed key as string
###############################################################################
function pproject::get_from_meta(){
    local searchstring="$1"
    if [ -e $meta_yaml_path ]; then
        while IFS='' read -r line || [[ -n "$line" ]]; do
            if [[ $line == *"$searchstring"* ]]; then
                echo $( echo "$line" | cut -d' ' -f 6-)
            fi
        done < $meta_yaml_path;
    fi
}


###############################################################################
# Collects the name of the environment from the meta.yaml file.
###############################################################################
function pproject::get_envname_from_meta(){
    echo $(pproject::get_from_meta "name:")
}


###############################################################################
# This function is supposed to be added to your precmd (.zshrc/.bashrc).
# function used for automated conda environment activation in shell (zsh/bash)
# if cwd contains conda-build/meta.yaml file.
# For detailed information about how to use this function see the README.md
# file.
# -----------------------------------------------------------------------------
# Globals:
#     $PWD
#     $PYTHONPATH
#     $AUTOACTIVATE
#     $meta_yaml_md5_path
#     $meta_yaml_path
###############################################################################
function pproject::autoactivate_env() {
    pproject_py="$pproject_env/bin/pproject_py"
    if (( $AUTOUPDATE == 0 )); then
        if [ -e $PWD/$meta_yaml_md5_path ]; then
            local new_md5=$(echo "$(md5sum $PWD/$meta_yaml_path)" | cut -d' ' -f1)
            local current_md5="$(head -n 1 $PWD/$meta_yaml_md5_path)"
            if ! [ $new_md5 = $current_md5 ]; then
                source deactivate
                pproject::log "AU" "info" "meta.yaml changed => Update."
                if $pproject_py update; then
                    pproject::log "AU" "F"
                else
                    pproject::log "AU" "x"
                fi
            fi
        fi
    fi

    if (( $AUTOACTIVATE == 0 )); then
        if [ -e $PWD/$meta_yaml_path ]; then
            local env="$(pproject::get_envname_from_meta)"
            local env="${env%\"}"
            local env="${env#\"}"
            if [[ $PATH != *$env* ]]; then
                if source activate $env 2>/dev/null && [[ $? -eq 0 ]]; then
                    CONDA_ENV_ROOT="$(pwd)"
                    PYTHONPATH=.:$PYTHONPATH
                    pproject::log "A" "info" "Activated"
                fi
            fi
        elif [[ $PATH = */envs/* ]] && [[ $(pwd) != $CONDA_ENV_ROOT ]] \
          && [[ $(pwd) != $CONDA_ENV_ROOT/* ]]; then
            CONDA_ENV_ROOT=""
            source deactivate
            unset PYTHONPATH
            pproject::log "A" "info" "Deactivated"
        fi
    fi
}


###############################################################################
# This function is supposed to be called from terminal (zsh/bash).
# Toggles the AUTOACTIVATE variable. If it is activated it will be deactivated
# if this function is called and vice versa.
# -----------------------------------------------------------------------------
# Globals:
#     $AUTOACTIVATE
###############################################################################
function pproject::autoactivate_toggle(){
    if (( $AUTOACTIVATE == 1 )); then
        export AUTOACTIVATE=0
        pproject::log "A" "info" '\033[1;92m'"on"'\033[0m';
    else
        export AUTOACTIVATE=1
        pproject::log "A" "info" '\033[1;91m'"off"'\033[0m';
    fi
}
###############################################################################
# This function is supposed to be called from terminal (zsh/bash).
# Toggles the AUTOACTIVATE variable. If it is activated it will be deactivated
# if this function is called and vice versa.
# -----------------------------------------------------------------------------
# Globals:
#     $AUTOACTIVATE
###############################################################################
function pproject::autoupdate_toggle(){
    if (( $AUTOUPDATE == 1 )); then
        export AUTOUPDATE=0
        pproject::log "AU" "info" '\033[1;92m'"on"'\033[0m';
    else
        export AUTOUPDATE=1
        pproject::log "AU" "info" '\033[1;91m'"off"'\033[0m';
    fi
}


###############################################################################
# This function acts like the interface between the pproject-python and the bash-
# functions inside this file.
# The bash functions are required for the activation of conda-environments
# in the current terminal. All other functionality is supposed to be served
# from the python-script.
# -----------------------------------------------------------------------------
# Globals:
#     $PWD
#     $meta_yaml_path
#     $meta_yaml_md5_path
#     $pproject_env
###############################################################################
function pproject(){
    pproject_py="$pproject_env/bin/pproject_py"
    tool=$1
    shift
    case $tool in
        create)
            if ! $pproject_py create "$@"; then return 1; fi
            return 0;;
        version)
            if ! pproject::check_if_meta_yaml; then return 1; fi
            if ! $pproject_py version "$@"; then return 1; fi
            return 0;;
        update)
            # for the following the meta.yaml is required, so check if exists.
            if ! pproject::check_if_meta_yaml; then return 1; fi
            if ! $pproject_py update; then return 1; fi
            return 0;;
        # TODO: implement "project build {package, container}"
        build)
            # for the following the meta.yaml is required, so check if exists.
            if ! pproject::check_if_meta_yaml; then return 1; fi
            if ! $pproject_py build "$@"; then return 1; fi
            return 0;;
        test)
            # for the following the meta.yaml is required, so check if exists.
            if ! pproject::check_if_meta_yaml; then return 1; fi
            if ! $pproject_py test; then return 1; fi
            return 0;;
        release)
            # for the following the meta.yaml is required, so check if exists.
            if ! pproject::check_if_meta_yaml; then return 1; fi
            if ! $pproject_py release "$@"; then return 1; fi
            return 0;;
        info)
            # for the following the meta.yaml is required, so check if exists.
            if ! $pproject_py info "$@"; then return 1; fi
            return 0;;
        sphinx)
            if ! $pproject_py sphinx; then return 1; fi
            return 0;;
        help)
            $pproject_py "--help"
            return 0;;
        autoenv) pproject::autoactivate_env; return 0;;
        autoenv_toggle) pproject::autoactivate_toggle; return 0;;
        autoupdate_toggle) pproject::autoupdate_toggle; return 0;;
    esac
}
