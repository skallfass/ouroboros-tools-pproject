# -*- coding: utf-8 -*-

"""
Copyright (C) 2018 Simon Kallfass

Utils used by the pproject-module like md5sum-calculations, config-loading,
executing commands in bash and ssh-interactions.
"""

import hashlib
from pathlib import Path
import socket
import subprocess
from subprocess import check_output

import paramiko
import yaml

from ouroboros.tools.pproject.validators import SConfig
from ouroboros.tools.pproject import inform


# -----------------------------------------------------------------------------
def load_configs(default_config_path=None, user_config_path=None):
    """
    Unwritten yet

    Parameters
    ----------
    default_config_path: pathlib.Path
    user_config_path: pathlib.Path

    Returns
    -------
    list:
        List of dicts containing "default_config"-content and
        "user_config"-content.
    """
    config = {}
    if not default_config_path:
        default_config_path = (Path(__file__).absolute()
                               .with_name('pproject_config.yml'))
    if not user_config_path:
        user_config_path = Path.home() / '.config/pproject/pproject_config.yml'
    assert all([isinstance(default_config_path, Path),
                isinstance(user_config_path, Path)])
    with open(str(default_config_path)) as default_conf:
        default_config = yaml.load(default_conf)
        SConfig(strict=True).load(default_config)
    if user_config_path.exists():
        with open(user_config_path) as conf:
            user_config = yaml.load(conf)
            SConfig(strict=True).load(user_config)
    else:
        user_config = {}
    for config_key, config_value in default_config.items():
        config[config_key] = user_config.get(config_key) or config_value
    SConfig(strict=True).load(config)
    return config


# -----------------------------------------------------------------------------
def get_config_for_terminal():
    """
    Reads the config file of pproject and prints the content.
    Used to source the config variables inside the pproject.sh script.

    Parameters
    ----------
    path: pathlib.Path
        The path of the config file.
    """
    for key, val in load_configs().items():
        if not isinstance(val, dict) and not isinstance(val, list):
            print(f'{key}={val}')


# -----------------------------------------------------------------------------
def md5(fname):
    """
    Calculates the md5sum of the passed file and returns the calculated value.

    Parameters
    ----------
    fname: str
        filename of file to calculate the md5sum for

    Returns
    --------
    str
        md5sum of passed file
    """
    hash_md5 = hashlib.md5()
    if isinstance(fname, str):
        fname = Path(fname)
    assert isinstance(fname, Path)
    assert fname.exists()
    with open(str(fname), "rb") as file_of_interest:
        for chunk in iter(lambda: file_of_interest.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# -----------------------------------------------------------------------------
def run_in_bash(command):
    """
    Executes a passed command in bash.

    Parameters
    ----------
    command: str
        command to be executed inside bash

    Returns
    -------
    result: str
        Result for executed command
    """
    result = check_output([f'/bin/bash -c "{command}"'],
                          shell=True,
                          stderr=subprocess.STDOUT).strip().decode('utf-8')
    return result


# -----------------------------------------------------------------------------
def connect_ssh(dst):
    """
    Connect to destination host (dst).

    Parameters
    ----------
    dst: str
        The destination-host as combination of "username@hostname".

    Returns
    -------
    paramiko.SSHClient
        The connection-object to the dst-host.
    """
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    username, hostname = dst.split('@')
    try:
        ssh.connect(hostname, 22, username, look_for_keys=True, compress=True)
    except paramiko.ssh_exception.AuthenticationException:
        inform.error('Authentication failed')
        inform.critical()
    except socket.gaierror:
        inform.error('Name or service not known')
        inform.critical()
    else:
        return ssh
