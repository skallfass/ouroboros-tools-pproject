# -*- coding: utf-8 -*-

"""
Copyright (C) 2018 Simon Kallfass

The pproject-module provides the functionality and logic used by the
pproject.sh-file.
"""


import argparse
import datetime as dt
import logging
import os
from pathlib import Path
import string
import sys
from subprocess import CalledProcessError
from pkg_resources import get_distribution

import attr
from cookiecutter.main import cookiecutter
from marshmallow import ValidationError

from ouroboros.tools.pproject import inform
from ouroboros.tools.pproject import git
from ouroboros.tools.pproject import utils
from ouroboros.tools.pproject import conda
from ouroboros.tools.pproject import validators
from ouroboros.tools.pproject import sphinx


try:
    __version__ = get_distribution('ouroboros-tools-pproject').version
except:
    __version__ = ''

for name, logger in logging.root.manager.loggerDict.items():
    logging.getLogger(name).setLevel(logging.WARNING)

CONFIG = utils.load_configs()
VCS_SETTINGS = CONFIG['vcs'][CONFIG['vcs']['use']]
OFFLINE_NAMESPACES = VCS_SETTINGS['offline_namespaces']


# =============================================================================
@attr.s
class Project:
    """
    Class representing an pproject-project. It contains methods to create new
    projects with cookiecutter, update project-environment, test defined tests
    with pytest, build a conda-package from the project, increase projects
    git-tag based on semantic versioning, release of the project as a
    conda-package in its on environment on another host.

    Attributes
    ----------
    company: str
        The name of the company to use in the project.
    namespace: str
        The namespace in which the project is placed.
    project: str
        The name of the project.
    pythonversion: str
        The pythonversion to use inside the project.
    username: str
        The name of the author of the project (collected by git config).
    email: str
        The email of the author of the project (collected by git config).
    year: str
        The year in which the project was created.
    today: str
        The date when the project was created.
    version: str
        The current git tag of the project.  Collected by git describe tag.
        Should be raised with "pproject new_version".
    environment: str
        The name of the conda-environment associated with the project.
        Either collected from meta.yaml if project already exists, or combined
        by "company-namespace-project" if created.
    git: git.GitRepo
        Enables git-interactions for project.
    """
    company = attr.ib()
    namespace = attr.ib()
    project = attr.ib()
    pythonversion = attr.ib()
    username = attr.ib(init=False)
    email = attr.ib(init=False)
    year = attr.ib(init=False)
    today = attr.ib(init=False)
    version = attr.ib(init=False, default=None)
    environment = attr.ib(init=False)
    path = attr.ib(default=Path.cwd())
    git = attr.ib(init=False, default=None)

    # -------------------------------------------------------------------------
    def __attrs_post_init__(self):
        envname = f'{self.company}-{self.namespace}-{self.project}'
        #if not envname in str(self.path):
        #    self.path = Path(self.path) / envname
        self.git = git.GitRepo(path=self.path)

    # -------------------------------------------------------------------------
    def update_informations(self, create=False, path=None):
        """
        Updates class-attributes with new informations collected from
        meta.yaml, git config and current datetime.

        Parameters
        ----------
        create: bool
            If project isn't created yet the name of the environment can't be
            extracted from the meta.yaml. In this case it has to be combined
            from companyname, namespace and projectname.
        path: pathlib.Path
            The projects-path.

        Note
        ----
        Uses :class:`conda.MetaYaml` to collect the name of environment
        from the current project if **create** is False.
        To collect git-specific informations :class:`git.GitRepo` is used.
        Checks for valid project-definition with :class:`validators.SProject`.
        """
        self.environment = f'{self.company}-{self.namespace}-{self.project}'
        if create:
            if not path:
                path = self.path.parent
            self.git = git.GitRepo(path=self.path)
        else:
            #if not self.environment in str(self.path):
            #    self.path = self.path / self.environment
            if not path:
                path = self.path
            meta_yaml = conda.MetaYaml(path=path / CONFIG['meta_yaml_path'])
            self.environment = meta_yaml.package_name
            self.git = git.GitRepo(path=self.path)
            self.version = self.git.get_tag()
        now = dt.datetime.now()
        self.year = now.strftime('%Y')
        self.today = now.strftime('%Y-%m-%d %H:%M')
        self.username = self.git.get_username()
        self.email = self.git.get_email()
        try:
            validators.SProject(strict=True).load(self.__dict__)
        except ValidationError as err:
            inform.error('Can\'t collect project information.')
            inform.error('Invalid value for following params:')
            for key, value in err.messages.items():
                inform.error(f'{key}: {value}')
            inform.critical()

    # -------------------------------------------------------------------------
    def create(self, on_vcs=False, path=None):
        """
        Creates new project based on a defined skeleton either local or on
        gitlab with cookiecutter, creates the base-conda-environment for
        developing the new project and manages corresponding git-tasks.

        Parameters
        ----------
        on_vcs: bool
            Flag to define if project should be added to remote vcs after
            creation.
        path: pathlib.Path
            The projects path.

        Note
        ----
        Calls :func:`Project.update_informations` with **create=True** to
        update the **attributes** of the project.
        For git operations the function :func:`utils.run_in_bash` is called.
        After creation :func:`Project.update` with **path** set to current
        working directory is called to create the conda-environment of the
        project.
        """
        if not path:
            path = self.path.parent
        self.update_informations(create=True, path=path)
        assert isinstance(path, Path)
        if not (path / self.environment).exists():
            if on_vcs:
                if not git.check_remote_vcs():
                    inform.error('Remote vcs not accessable')
                    inform.critical()
            inform.info(f'Creating project {self.environment}')
            cookiecutter(CONFIG['skeleton_repo'],
                         checkout=str(self.pythonversion),
                         output_dir=str(Path.cwd()),
                         no_input=True,
                         extra_context=self.__dict__)
            inform.info('Created folder')
            os.chdir(str((path / self.environment).absolute()))
            if not self.environment in str(self.path):
                self.path = self.path / self.environment
            self.git = git.GitRepo(path=self.path)
            if on_vcs:
                create_on_remote_res = git.create_on_remote_vcs(
                    company=self.company,
                    namespace=self.namespace,
                    project=self.project,
                    username=self.git.get_username())
            inform.info('Initializing git')
            self.git.initialize()
            inform.info('Adding files')
            self.git.add_all()
            inform.info('Commiting')
            self.git.commit()
            vcs_ssh = VCS_SETTINGS['ssh']
            vcs = CONFIG['vcs']['use']
            vcs_use_groups = VCS_SETTINGS['use_groups']
            if on_vcs:
                if vcs == 'gitlab' and vcs_use_groups:
                    git_repo = f'{create_on_remote_res}/{self.project}.git'
                else:
                    git_repo = f'{create_on_remote_res}.git'
                if ':' in vcs_ssh:
                    git_origin = f'{vcs_ssh}/{git_repo}'
                else:
                    git_origin = f'{vcs_ssh}:{git_repo}'
                inform.info(f'Setting origin to {git_origin}')
                self.git.set_origin(git_origin)
                inform.info(f'Pushing to origin')
                self.git.push_to_branch('master')
            inform.finished()
            self.update(path=(path / self.environment).absolute())
        else:
            inform.error('Folder already exists')
            inform.critical()

    # -------------------------------------------------------------------------
    def update(self, path=None):
        """
        Updates the project-related conda-environment.
        If it already exists it will be removed and then recreated.
        This ensures to remove dependencies of packages which aren't required
        anymore.
        If the environment doesn't exist yet, the environment will be created.
        Finally stores the md5sum of the based meta.yaml file inside a file
        to enable the pproject-autoenv functionality triggered by changes
        inside the meta.yaml file.

        Parameters
        ----------
        path: str
            Path of the required meta.yaml file. Only required if the meta.yaml
            is outside of the current working directory

        Note
        ----
        The pythonversion and the dependencies are collected with
        :class:`conda.MetaYaml`. Environment creation/removal is done using
        :class:`conda.CondaEnvironment`.
        To calculate the new md5sum of the meta.yaml and store it inside the
        hash.md5-file, :func:`update_md5sum` is used.
        """
        self.update_informations()
        if not path:
            path = self.path
        inform.info(f'Environment: {self.environment}')
        inform.info('Updating env')
        meta_yaml = conda.MetaYaml(path=path / CONFIG['meta_yaml_path'])
        self.pythonversion = meta_yaml.pythonversion
        env = conda.CondaEnvironment(name=self.environment)
        if env.exists():
            inform.info('Removing env')
            env.remove()
        inform.info('Creating env')
        env.create(dependencies=meta_yaml.dependencies)
        self.update_md5sum()
        inform.finished()

    # -------------------------------------------------------------------------
    def test(self, path=None):
        """
        Runs all tests for the project in its tests folder with pytest.

        Parameters
        ----------
        path: pathlib.Path
            The projects path.

        Note
        ----
        Calls :func:`Project.test` to update the projects conda-environment
        before running the tests with pytest.
        """
        if not path:
            path = self.path
        self.update()
        inform.info('Running tests for project with pytest')
        # using bash cause importing pytest in sublevels (testing pproject
        # itself) can be pain in the ass
        try:
            res = utils.run_in_bash(
                f'{Path(CONFIG["pproject_env"]) / "bin/pytest"} '
                f'{" ".join(CONFIG["pytest_arguments"])} {path}')
            print(res)
        except CalledProcessError as err:
            print(err.output.strip().decode('ascii'))
            inform.critical()
        inform.finished()

    # -------------------------------------------------------------------------
    def build(self, publish=False, path=None):
        """
        Builds a conda-package from the project.
        First it runs all tests to ensure functionality of the resulting
        package. Assuming the test-coverage is acceptable.
        Then it checks for uncommited stuff inside the project and if it is
        tagged with a version-tag.  Finally the conda-package is build.
        If the publish-flag is set it is uploaded to the conda-repo-server.
        Else it is only built local.

        Parameters
        ----------
        publish: bool
            Flag which indicates if the resulting conda-package should be
            uploaded to the conda-repository-server defined in the config-file
            or not.
        path: pathlib.Path
            The projects path.

        Note
        ----
        Runs :func:`Project.test` before build to check for failures.
        Checks if uncommited stuff remains inside project-folder before build
        with :func:`check_git_status`.
        Also checks if a required git-tag exists with :func:`get_git_tag`.
        To execute the conda-build command :func:`utils.run_in_bash` is used.
        """
        if not path:
            path = self.path
        self.update_informations()
        self.test(path=path)
        checks = all([self.git.status(),
                      self.git.get_tag(),
                      self.git.check_tag_on_remote()])
        if checks:
            inform.info(f'Started build of {self.environment}')
            pkg_name = conda.build_package(path=path,
                                           pythonversion=self.pythonversion,
                                           simulate=True)
            inform.info(f'Returning packagename will be {pkg_name}')
            try:
                pkg_file = conda.build_package(
                    path=path,
                    pythonversion=self.pythonversion)
                bld_path = Path(CONFIG['conda_folder']) / 'conda-bld/linux-64'
                pkg_path = str(bld_path / pkg_file)
                inform.info(f'Built package is {localfilepath}')
                if publish:
                    conda.publish_package_on_reposerver(pkg_path)
                inform.finished()
            except CalledProcessError:
                inform.critical()
        else:
            inform.error('Git-status not clean.Check git status and tag.')
            inform.critical()

    # -------------------------------------------------------------------------
    def new_version(self, vtype, message='New version triggered by pproject',
                    path=None):
        """
        Raises the passed vtype (versiontype) inside version (git-tag) of the
        project.
        Version has to be in semantic versioning style (see https://semver.org/
        for details).
        Example for version in semantic versioning style:
        General: "major.minor.patch"
        Example: "1.0.1"

        Parameters
        ----------
        vtype: str
            The part to raise inside current version. Valid are: "major",
            "minor" and "patch"
        message: str
            The message to use for the git tag.
        path_: pathlib.Path()
            The projects path.

        Note
        ----
        First checks if there is uncommited stuff inside the current branch.
        If there is uncommited stuff, the operation is aborted.
        Else checks if the gitlab is reachable.
        Then the current version is collected.
        The passed **vtype** is raised by 1. Finally the resulting version-tag
        is added with passed **message** and the new tag is pushed to gitlab.
        For these operations :class:`git.GitRepo` is used.
        """
        if not path:
            path = self.path
        assert all([isinstance(vtype, str), isinstance(message, str)])
        assert vtype in ('major', 'minor', 'patch')
        self.update_informations(path=path)
        if self.git.status():
            if not git.check_remote_vcs():
                inform.error('Remote vcs not accessable')
                inform.critical()
            else:
                self.version = self.git.get_tag()
                inform.info(f'Current version is {self.version}')
                major, minor, patch = [
                    int(_) for _ in self.version.split('-')[0].split('.')]
                vrs = {'major': major, 'minor': minor, 'patch': patch}
                vrs[vtype] += 1
                if vtype != 'patch':
                    vrs['patch'] = 0
                    if vtype == 'major':
                        vrs['minor'] = 0
                res_version = f'{vrs["major"]}.{vrs["minor"]}.{vrs["patch"]}'
                inform.info(f'Resulting version {res_version}')
                try:
                    self.git.create_tag(res_version, message)
                    self.git.push_tag(res_version)
                except CalledProcessError:
                    inform.error('Can\'t push to remote vcs.')
                    inform.critical()
                self.version = res_version
        else:
            inform.error(
                'No new git-tag possible, uncommited stuff in project')
            inform.critical()

    # -------------------------------------------------------------------------
    def info(self, path=None):
        """
        Collects and prints information about the pproject-configuration and
        the current project.

        Parameters
        ----------
        path: pathlib.Path
            The projects path.

        Note
        ----
        Uses :class:`conda.MetaYaml` to collect the project informations.
        The current version is collected by :func:`get_git_tag`.
        Resulting packagename is collected by
        :func:`conda.build_package`.
        The pproject-settings are collected by the global variables.
        """
        if not path:
            path = self.path
        meta_yaml = conda.MetaYaml()
        dependencies = f'- {meta_yaml.dependencies[0]}'
        for dep in meta_yaml.dependencies[1:]:
            try:
                search = (dep
                          .replace("<", "")
                          .replace(">", "")
                          .replace("=", "")
                          .replace(" ", "="))
                utils.run_in_bash(
                    f'{Path(CONFIG["conda_folder"]) / "bin/conda"} search '
                    f'{search}')
                dependencies += f'\n{"." * 26} - {dep}'
            except CalledProcessError:
                dependencies += (f'\n{"." * 26} {inform.RED}- {dep} '
                                 f'(not available in channels){inform.NCOLOR}')
        project_infos = [
            '',
            ' PROJECT INFO'.rjust(80, '='),
            f'{" name".rjust(26, ".")}  {self.environment}',
            f'{" reponame".rjust(26, ".")}  {self.environment}',
            f'{" current version-tag".rjust(26, ".")}  {self.git.get_tag()}',
            f'{" pythonversion".rjust(26, ".")}  {self.pythonversion}',
            f'{" dependencies".rjust(26, ".")} {dependencies}',
            '']
        for project_info in project_infos:
            print(f'{inform.BOLD}{project_info}{inform.NCOLOR}')

    # -------------------------------------------------------------------------
    def release(self, dst='localhost', envname=None, path=None):
        """
        Rolls out the current project as a conda-package in its own
        conda-environment either on localhost or on a remote.

        Parameters
        ----------
        dst: str
            The destination where the resulting package should be rolled out.
            Valid values are: "localhost" (default), "USER@HOSTNAME"
        envname: str
            The name of the environment to create on destination with the
            resulting package. If no "environment" is passed, the name of the
            project-environment is used.
        path: pathlib.Path
            The projects path.

        Note
        ----
        The version of the project is collected by :func:`get_git_tag`.
        Then the project is build as a conda-package with
        :func:`Project.build`. If **destination** is "localhost", the creation
        of the conda-envrionment for the just created package is done by
        :func:`utils.run_in_bash`. Else the required commands are executed by
        paramiko.
        """
        if not path:
            path = self.path
        envname = envname or f'{self.environment}_env'
        self.build(path=path)
        self.update_informations(path=path)
        inform.info(f'Env: {envname}')
        if dst == 'localhost':
            env = conda.CondaEnvironment(name=envname)
            # TODO: use recreate
            if env.exists():
                inform.info('Removing env (already exists)')
                env.remove()
            inform.info('Creating env')
            env.create(dependencies=[f'python={self.pythonversion}',
                                     f'{self.environment}={self.version}'])
        else:
            env = conda.CondaEnvironment(name=envname)
            env.create_remote(ssh=utils.connect_ssh(dst),
                              pythonversion=self.pythonversion,
                              packagename=self.environment,
                              version=self.version,
                              projectpath=self.path)
        inform.finished()

    # -------------------------------------------------------------------------
    def sphinx(self, path=None):
        """
        Creates a sphinx documentation for the current pproject project.

        Parameters
        ----------
        path: pathlib.Path
            The projects path.
        """
        if not path:
            path = self.path
        if not (path / 'source').exists() and not (path / 'build').exists():
            sphinx.run_sphinx_quickstart(path=path,
                                         environment=self.environment,
                                         username=self.username,
                                         version=self.version)
            sphinx.customize_config(path=path)

        sphinx.create_coverage_badge(path=path, environment=self.environment)
        sphinx.update_source(path=path)
        sphinx.make_documentation(path=path)
        inform.info('Generated html-files in "build"')
        inform.finished()

    # -----------------------------------------------------------------------------
    def update_md5sum(self):
        inform.info('Storing new md5sum of meta.yaml')
        ((self.path / CONFIG['meta_yaml_md5_path'])
         .open('w')
         .write(utils.md5(str(self.path / CONFIG['meta_yaml_path']))))


# -----------------------------------------------------------------------------
def general_info():
    """
    Collects and prints information about the pproject-configuration and the
    current project.

    Note
    ----
    The pproject-settings are collected by the global variables.
    """
    # -------------------------------------------------------------------------
    def justify_key(key, length=25):
        return f'{key.rjust(length, ".")}'

    # -------------------------------------------------------------------------
    def bold(value):
        return f'{inform.BOLD}{value}{inform.NCOLOR}'

    # -------------------------------------------------------------------------
    def create_table_content(content, tbl, before=0):
        for key, val in content.items():
            length = 25 if before == 0 else before + 15
            if not isinstance(val, dict):
                tbl.append(f'{justify_key(key, length=length)}  {bold(val)}')
            else:
                tbl.append(justify_key(key, length=length))
                create_table_content(content=val, tbl=tbl, before=before+15)
        return tbl

    autosts = {'AUTOACTIVATE': None,
               'AUTOUPDATE': None}
    for astate in autosts:
        if int(utils.run_in_bash(f'echo ${astate}')) == 0:
            autosts[astate] = f'{inform.GREEN}on{inform.NCOLOR}'
        else:
            autosts[astate] = f'{inform.RED}off{inform.NCOLOR}'
    pproject_infos = ['',
                      ' GENERAL PPROJECT-INFO'.rjust(80, '='),
                      f'{justify_key("version")}  {bold(__version__)}',
                      f'{justify_key("autoenv")}  {autosts["AUTOACTIVATE"]}',
                      f'{justify_key("autoupdate")}  {autosts["AUTOUPDATE"]}',
                      '',
                      ' CONFIG'.rjust(80, '=')]
    pproject_infos.extend(
        create_table_content(utils.load_configs(), []) + [''])

    vcs = CONFIG['vcs']['use']
    if vcs == 'gitlab' and VCS_SETTINGS['use_groups']:
        namespaces_info = [' NAMESPACES'.rjust(80, "="),]
        try:
            raw_gitlab_groups = git.get_gitlab_groups()
            namespaces_info.append(f'{justify_key("GROUP")}  ID')
            available_namespaces = {
                grp.split('-')[1]: grp_id
                for grp, grp_id
                in raw_gitlab_groups.items()
                if '-' in grp and grp.split('-')[0] == CONFIG['company']}
            for grp, grp_id in available_namespaces.items():
                namespaces_info.append(
                    f'{bold(justify_key(grp))}  {bold(grp_id)}')
            pproject_infos.extend(namespaces_info + [''])
        except Exception:
            pass

    for pproject_info in pproject_infos:
        print(f'{inform.CYAN}{pproject_info}{inform.NCOLOR}')


# -----------------------------------------------------------------------------
def build_arguments(args):
    """
    The argument parsing for the python-part of the pproject-tool.

    Parameters
    ----------
    args: list

    Returns
    -------
    parsed_args: argparse.Namespace
    """
    # TODO: make dynamic with CONFIG['use_vcs']
    try:
        assert all([_ in (list(string.ascii_letters) + ['_'])
                    for _ in list(CONFIG['company'])])
    except AssertionError:
        inform.error('Your company-name contains unsupported chars (only letters and "_" are allowed)')
        inform.critical()
    vcs = CONFIG['vcs']['use']
    if vcs == 'gitlab' and VCS_SETTINGS['use_groups']:
        try:
            available_namespaces = [
                grp.split('-')[1]
                for grp
                in git.get_gitlab_groups().keys()
                if '-' in grp and grp.split('-')[0] == CONFIG['company']]
            if not available_namespaces:
                raise AttributeError
        except:
            available_namespaces = OFFLINE_NAMESPACES
    else:
        available_namespaces = OFFLINE_NAMESPACES
    parser = argparse.ArgumentParser(description='ouroboros-tools-pproject')
    tools = parser.add_subparsers(
        description='pproject supports different tools. These are:')
    create = tools.add_parser(
        'create',
        description='creates new pproject supported project')
    create.set_defaults(tool='create')
    create.add_argument('-r', '--remote', action='store_true', default=False)
    namespaces = create.add_subparsers(
        description='the following namespaces are supported')
    #for namespace_name in ('services', 'products', 'modules', 'operations'):
    for namespace_name in available_namespaces:
        namespace = namespaces.add_parser(
            namespace_name,
            description=f'Uses "{namespace_name}" as namespace')
        namespace.set_defaults(namespace=namespace_name)
        namespace.add_argument('-n', '--projectname', type=str, required=True)
        namespace.add_argument('-p',
                               '--pythonversion',
                               type=str,
                               default='3.6')
    build = tools.add_parser('build')
    build.set_defaults(tool='build')
    build.add_argument('-p', '--publish', action='store_true', default=False)
    for tool in ('test', 'sphinx', 'update'):
        new_tool = tools.add_parser(tool)
        new_tool.set_defaults(tool=tool)
    info_parser = tools.add_parser('info')
    info_parser.set_defaults(tool='info')
    infotypes = info_parser.add_subparsers()
    info_general = infotypes.add_parser('general')
    info_general.set_defaults(infotype='general')
    info_project = infotypes.add_parser('project')
    info_project.set_defaults(infotype='project')
    new_version = tools.add_parser('version')
    new_version.add_argument('-m', '--message', type=str, required=True)
    new_version.set_defaults(tool='version')
    versiontypes = new_version.add_subparsers()
    for versiontype in ('major', 'minor', 'patch'):
        vtype = versiontypes.add_parser(versiontype)
        vtype.set_defaults(versiontype=versiontype)
    release = tools.add_parser('release')
    release.set_defaults(tool='release')
    release.add_argument('-d', '--userathost', type=str)
    release.add_argument('-e', '--envname', type=str)
    return parser.parse_args(args)


# -----------------------------------------------------------------------------
def run(options, path=Path.cwd()):
    """
    Parameters
    ----------
    options: argparse.Namespace
    path: pathlib.Path
    """
    if options.tool == 'info':
        if options.infotype == 'general':
            general_info()
        elif options.infotype == 'project':
            try:
                meta_yaml = conda.MetaYaml()
                company, namespace, projectname = (meta_yaml.package_name
                                                   .split('-'))
                pythonversion = meta_yaml.pythonversion
                prj = Project(company=company,
                              namespace=namespace,
                              project=projectname,
                              pythonversion=pythonversion,
                              path=path)
                prj.update_informations(create=True, path=path)
                prj.info()
            except Exception as err:
                print(err)
                inform.error('Not a valid pproject-project!')
                inform.critical()
    else:
        if options.tool not in ('create',):
            meta_yaml = conda.MetaYaml()
            company, namespace, projectname = meta_yaml.package_name.split('-')
            pythonversion = meta_yaml.pythonversion
        else:
            company, namespace, projectname = [CONFIG['company'],
                                               options.namespace,
                                               options.projectname]
            pythonversion = options.pythonversion
        prj = Project(company=company,
                      namespace=namespace,
                      project=projectname,
                      pythonversion=pythonversion,
                      path=path)
        if options.tool == 'update':
            prj.update_informations()
            prj.update()
        elif options.tool == 'test':
            prj.update_informations()
            prj.test(path=path)
        elif options.tool == 'sphinx':
            prj.update_informations()
            prj.sphinx()
        elif options.tool == 'create':
            prj.create(on_vcs=options.remote,
                       path=path)
        elif options.tool == 'build':
            prj.update_informations()
            prj.build(publish=options.publish)
        elif options.tool == 'version':
            prj.update_informations()
            prj.new_version(vtype=options.versiontype,
                            message=options.message)
        elif options.tool == 'release':
            try:
                envname = options.envname
            except:
                envname = f'{Path.cwd().name}_env'
            prj.update_informations()
            prj.release(dst=options.userathost,
                        envname=envname)


# -----------------------------------------------------------------------------
def main():
    """
    The main function coordinating the python-part of the pproject-tool.
    Creates default-config inside ~/.config/pproject if it doesn't exist.

    Note
    ----
    The arguments are parsed by :func:`build_arguments`.
    All other operations are done by :class:`conda.MetaYaml` and
    :class:`Project` and their methods.
    """
    userconfig = Path.home() / '.config/pproject/pproject_config.yml'
    if not userconfig.parent.exists():
        userconfig.parent.mkdir(parents=True)
        defaultconfig = Path(__file__).with_name('pproject_config.yml')
        with defaultconfig.open('rb') as dconfig:
            userconfig.write_bytes(dconfig.read())
    options = build_arguments(sys.argv[1:])
    run(options)
    sys.exit(0)


# =============================================================================
if __name__ == '__main__':
    main()
