# -*- coding: utf-8 -*-

"""
Copyright (C) 2018 Simon Kallfass

conda-commands used by the pproject-module.
"""

import datetime as dt
import getpass
import os
from pathlib import Path
import socket
from subprocess import CalledProcessError

import attr
import jinja2
from marshmallow import ValidationError
from ruamel.yaml import YAML
import six

from ouroboros.tools.pproject import git
from ouroboros.tools.pproject import inform
from ouroboros.tools.pproject import utils
from ouroboros.tools.pproject import validators


CONFIG = utils.load_configs()
CONDA_BIN = Path(CONFIG['conda_folder']) / 'bin/conda'
CONDA_REPO_SETTINGS = CONFIG['conda_respository_server']


# =============================================================================
@attr.s
class MetaYaml:
    """
    Class representing the meta.yaml file of a python-conda-package.
    Includes a get_content-method for reading the content of the meta.yaml-file
    and a update-method which calls the get_content-method and updates
    the class-attributes with the collected informations.

    Attributes
    ----------
    path: str
    content: dict
    dependencies: dict
    pythonversion: str
    package_name: str
    """
    path = attr.ib(default=None)
    content = attr.ib(init=False)
    dependencies = attr.ib(init=False)
    pythonversion = attr.ib(init=False)
    package_name = attr.ib(init=False)

    def __attrs_post_init__(self):
        """
        Updates the class-attributes and validates the contents of the
        meta.yaml-file.
        """
        if not self.path:
            self.path = Path.cwd() / CONFIG['meta_yaml_path']
        if not self.path.exists():
            raise AttributeError(f'Path {self.path} doesn\'t exist.')
        self.update()
        try:
            validators.SMetaYaml(strict=True).load(self.get_content())
        except ValidationError as err:
            inform.error('meta.yaml has incorrect content.')
            inform.error('Invalid value for following params:')
            for key, value in err.messages.items():
                inform.error(f'{key}: {value}')
            inform.critical()

    def update(self):
        """
        Updates the class-attributes with informations collected by the
        get_content-method.

        Note
        ----
        Uses method :func:`MetaYaml.get_content` to collect the content of the
        meta.yaml file.
        """
        self.content = self.get_content()
        self.dependencies = self.content['requirements']['run']
        self.pythonversion = self.content['extra']['pythonversion']
        self.package_name = self.content['package']['name']

    def get_content(self):
        """
        Collects the contents of the meta.yaml file and returns the collected
        informations.

        Returns
        -------
        content: dict
            Contents of the meta.yaml file.
        """
        # =====================================================================
        class NullUndefined(jinja2.Undefined):
            """
            Class required to handle jinja2-variables inside the meta.yaml
            """
            # -----------------------------------------------------------------
            def __unicode__(self):
                return six.text_type(self._undefined_name)

            # -----------------------------------------------------------------
            def __getattr__(self, attribute_name):
                return six.text_type(f'{self}.{attribute_name}')

            # -----------------------------------------------------------------
            def __getitem__(self, attribute_name):
                return f'{self}["{attribute_name}"]'


        # =====================================================================
        class StrDict(dict):
            """
            Class required to handle jinja2-variables inside the meta.yaml
            """
            # -----------------------------------------------------------------
            def __getitem__(self, key, default=''):
                return self[key] if key in self else default

        return YAML(typ='base').load(
            (jinja2.Environment(undefined=NullUndefined)
             .from_string(self.path.open().read())
             .render(**dict(os=os,
                            environ=StrDict(),
                            load_setup_py_data=StrDict))))


# =============================================================================
@attr.s
class CondaEnvironment:
    """
    Class representing a conda-environment.
    Includes methods for creation, removal (local and remote) of the
    conda-environment.
    """
    name = attr.ib()
    path = attr.ib(init=False)

    # -------------------------------------------------------------------------
    def __attrs_post_init__(self):
        """
        Method to be called after initialization of the class.
        Combines self.path from conda-folder as defined in the pproject-config
        with "envs" and conda-environments name as defined in self.name.
        """
        self.path = (Path(CONFIG['conda_folder']) / 'envs' / self.name)

    # -------------------------------------------------------------------------
    def exists(self):
        """
        Check if conda-environment with name self.name exists.

        Returns
        -------
        bool
            True if conda-environment exists, else False.
        """
        return self.path.exists()

    # -------------------------------------------------------------------------
    def remove(self):
        """
        Remove conda-environment with name self.name if it exists.
        """
        if self.exists():
            try:
                utils.run_in_bash(
                    f'{CONDA_BIN} env remove -q -y -n {self.name}')
            except CalledProcessError as err:
                err_message = err.output.strip().decode('ascii')
                if 'CondaEnvironmentError:' in err_message:
                    inform.info('deactivating and retry')
                    utils.run_in_bash(
                        'source deactivate && '
                        f'{CONDA_BIN} env remove -q -y -n {self.name}')
                else:
                    inform.error('Couldn\'t remove environment. '
                                 'Following error occured:')
                    print(err_message)
                    inform.critical()

    # -------------------------------------------------------------------------
    def create(self, dependencies):
        """
        Create conda-environment with name self.name and passed dependencies.

        Parameters
        ----------
        dependencies: list
            List of strings with dependencies (packagename with optional
            version) to install inside environment.

            Example:
                ['python=3.6', 'attrs=>17.3']
        """
        deps = ' '.join([f"'{_}'"
                         .replace(' >=', '>=')
                         .replace(' <=', '<=')
                         .replace(' ', '=')
                         .replace('*', '')
                         for _ in dependencies])
        try:
            utils.run_in_bash(
                f'{CONDA_BIN} create -y -q -n {self.name} {deps}')
        except CalledProcessError as err:
            inform.error(f'Couldn\'t create environment {self.name}. '
                         'Following error occured:')
            print(err.output.strip().decode('ascii'))
            inform.error('Please check your meta.yaml-file and if '
                         'dependencies are available.')
            inform.critical()

    # -------------------------------------------------------------------------
    def recreate(self, dependencies):
        """
        Remove conda-environment if it already exists. Then creates new
        environment as self.name with passed dependencies.

        Parameters
        ----------
        dependencies: list
            List of strings with dependencies (packagename with optional
            version) to install inside environment.

            Example:
                ['python=3.6', 'attrs=>17.3']
        """
        self.remove()
        self.create(dependencies)

    # -------------------------------------------------------------------------
    def create_remote(self, ssh, pythonversion, packagename, version,
                      projectpath):
        """
        Release the package in its own conda-envrionment on a remote host.

        Parameters
        ----------
        ssh: paramiko.SSHClient
            Connection via ssh where the conda-environment should be created.
        pythonversion: str
            pythonversion to create the environment for.
        packagename: str
            Name of the package to install inside the created environment.
        version: str
            Version of the package to install inside the created environment.
        projectpath: str
            Path of currrent project.
        """
        inform.info('Creating env')
        cmd_create = (f'{CONDA_BIN} create -y -q -n {self.name} '
                      f'python={pythonversion} '
                      f'{packagename}={version}')
        _, stdout, stderr = ssh.exec_command(cmd_create)
        stdout.channel.recv_exit_status()
        err = stderr.read().strip().decode('ascii')
        if err:
            if 'CondaValueError: prefix already exists:' in err:
                inform.info('Recreating env')
                self.release_log(ssh, 'recreate', projectpath)
                self.remove_remote(ssh, projectpath)
                self.release_log(ssh, 'create', projectpath)
                _, stdout, stderr = ssh.exec_command(cmd_create)
                stdout.channel.recv_exit_status()
                err = stderr.read().strip().decode('ascii')
            else:
                inform.error(f'Error during rollout ({cmd_create} => {err})')
                inform.critical()
            if err:
                if not err.startswith('==> WARNING:'):
                    inform.error(f'Error during rollout ({cmd_create} => {err})')
                    inform.critical()
        else:
            self.release_log(ssh, 'create', projectpath)

    # -------------------------------------------------------------------------
    def remove_remote(self, ssh, projectpath):
        """
        Remove the conda-environment as defined in self.name via ssh from
        remote.

        Parameters
        ----------
        ssh: paramiko.SSHClient
            Connection via ssh where the conda-environment should be removed
            from.
        projectpath: str
            Path of currrent project.
        """
        inform.info('Removing env (already exists)')
        self.release_log(ssh, 'remove', projectpath)
        cmd_remove = (
            f'{CONDA_BIN} remove -y -q -n {self.name} --all')
        _, stdout, _ = ssh.exec_command(cmd_remove)
        stdout.channel.recv_exit_status()

    # -------------------------------------------------------------------------
    def release_log(self, ssh, action, projectpath):
        """
        Write information about ssh-interaction on the destination host as
        passed in ssh.

        ssh: paramiko.SSHClient
            Connection via ssh where to log the output to.
        action: str
            action as a string to log into the log-file.

            Example:
                "create"
        projectpath: str
            Path of currrent project.
        """
        git_repo = git.GitRepo(path=projectpath)
        log_entry = (f'{dt.datetime.utcnow().isoformat()} '
                     f'[{getpass.getuser()}@{socket.gethostname()}] '
                     f'{action.upper()} {self.name} '
                     f'[SOURCE: {git_repo.get_branch()} {git_repo.get_tag()}]')
        cmd = f'echo "{log_entry}" >> ~/.pproject.log'
        _, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()
        err = stderr.read().strip().decode('ascii')



# -----------------------------------------------------------------------------
def build_package(path, pythonversion, simulate=False):
    """
    Build conda-package from source at passed path for passed pythonversion.
    If simulate is set to True, the package isn't built. The function only
    returns the path of the resulting package if it would have been built.

    Parameters
    ----------
    path: pathlib.Path
        The path to the source for which the conda-package should be build.
    pythonversion: str
        The pythonversion to build the conda-package for.
    simulate: bool
        Flag if build is only simulated or not.

    Returns
    -------
    result: str
        The path of the resulting conda-package (simulated or real).
    """
    if simulate:
        pkg_name = utils.run_in_bash(
            f'cd {str(path.absolute())} && '
            f'{CONDA_BIN} build --python={pythonversion} --output {path}')
    else:
        utils.run_in_bash(f'cd {str(path.absolute())} && '
                          f'{CONDA_BIN} build --python={pythonversion} {path}')
        pkg_name = utils.run_in_bash(
            f'cd {str(path.absolute())} && '
            f'{CONDA_BIN} build --python={pythonversion} --output {path}')
    result = Path(pkg_name).name.rstrip()
    return result


# -----------------------------------------------------------------------------
def publish_package_on_reposerver(sourcepath):
    """
    Publish a conda-package from sourcepath on conda-repository-server as
    defined in the pprojects-config-file.

    Parameters
    ----------
    sourcepath: str
        Local path to the conda-package to publish on the
        conda-repository-server.
    """
    ssh = utils.connect_ssh(
        dst=f'{CONDA_REPO_SETTINGS["user"]}@{CONDA_REPO_SETTINGS["host"]}')
    ftp_client = ssh.open_sftp()
    ftp_client.put(sourcepath,
                   f'{CONDA_REPO_SETTINGS["packages_path"]}/'
                   f'{Path(sourcepath).name}')
    ftp_client.close()
    index_cmd = (f'{CONDA_REPO_SETTINGS["conda_exe"]} index '
                 f'{CONDA_REPO_SETTINGS["packages_path"]}')
    _, _, index_err = ssh.exec_command(index_cmd)
    index_err.channel.recv_exit_status()
