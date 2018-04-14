# -*- coding: utf-8 -*-

"""
Copyright (C) 2018 Simon Kallfass

git- and gitlab-commands used by the pproject-module.
"""


from pathlib import Path
from subprocess import CalledProcessError
import urllib

import attr
import requests

from ouroboros.tools.pproject import inform
from ouroboros.tools.pproject import utils


CONFIG = utils.load_configs()
VCS_SETTINGS = CONFIG['vcs'][CONFIG['vcs']['use']]


# -----------------------------------------------------------------------------
def check_remote_vcs():
    """
    Check if the vcs-url is reachable.

    Returns
    -------
    check_result: bool
        Result for the remote vcs to check.
    """
    try:
        status = urllib.request.urlopen(VCS_SETTINGS['url']).getcode()
        check_result = True if status == 200 else False
    except:
        check_result = False
    return check_result


# -----------------------------------------------------------------------------
def get_vcs_token():
    """
    Collect the users vcs-token from the token-file as defined in the config
    and return it.

    Returns
    -------
    token: str
        The vcs-token to interact with the remote vcs.
    """
    token_path = VCS_SETTINGS['token_path'].replace('~', str(Path.home()))
    with open(token_path, 'r') as tokenfile:
        token = tokenfile.readline().strip()
    return token


# -----------------------------------------------------------------------------
# TODO: make dynamic with use CONFIG['use_vcs']
def get_gitlab_groups():
    """
    Collect the available gitlab-groups for the gitlab-user and his
    gitlab-token from the defined gitlab-api.

    Returns
    -------
    gitlab_groups: dict
        Dict containing the available gitlab-groups.
    """
    glab_groups_info = requests.get(f'{VCS_SETTINGS["api"]}/groups',
                                    headers={'PRIVATE-TOKEN': get_vcs_token()})
    try:
        gitlab_groups = {_['name']: _['id'] for _ in glab_groups_info.json()}
    except TypeError:
        inform.error('No access to gitlab-api. Please check your token.')
        gitlab_groups = {}
    return gitlab_groups


# -----------------------------------------------------------------------------
def create_on_remote_vcs(*, company, namespace, project, username):
    """
    Create new project on remote vcs (as defined in config) based on the
    passed values "company", "namespace" and "project".

    Parameters
    ----------
    company: str
    namespace: str
    project: str
    username: str

    Returns
    -------
    project_to_create/gitlab_group: str
        The name of the created project / The name of the gitlab-group in
        which the project was created.
    """
    # TODO: returns what?
    assert check_remote_vcs()
    vcs = CONFIG['vcs']['use']
    api = VCS_SETTINGS['api']
    token = get_vcs_token()
    if vcs == 'gitlab':
        if VCS_SETTINGS['use_groups']:
            assert all([isinstance(_, str)
                        for _ in (company, namespace, project)])
            gitlab_groups = get_gitlab_groups()
            assert gitlab_groups
            gitlab_group = f'{company}-{namespace}'
            assert gitlab_group in gitlab_groups
            inform.info(f'Creating "{project}" on gitlab in "{gitlab_group}"')
            if len(api.split(':')) > 2:
                post_url = (f'{api}/projects?name={project}&'
                            f'namespace_id={gitlab_groups[gitlab_group]}')
            else:
                post_url = (f'{api}:projects?name={project}&'
                            f'namespace_id={gitlab_groups[gitlab_group]}')
            requests.post(post_url,
                          headers={'PRIVATE-TOKEN': token})
            return gitlab_group
        else:
            project_to_create = f'{company}-{namespace}-{project}'
            inform.info(f'Creating {project_to_create} on {vcs}')
            if len(api.split(':')) > 2:
                post_url = (f'{api}/projects?private_token={token}')
            else:
                post_url = (f'{api}:projects?private_token={token}')
            requests.post(post_url,
                          headers={'Content-Type': 'application/json'},
                          json=dict(name=project_to_create))
            return project_to_create
    elif vcs == 'github':
        project_to_create = f'{company}-{namespace}-{project}'
        inform.info(f'Creating {project_to_create} on {vcs}')
        requests.post(api,
                      auth=(username, token),
                      json=dict(name=project_to_create))
        return project_to_create


# =============================================================================
@attr.s
class GitRepo:
    """
    Class representing a local git-repository.
    Includes methods to check its status, initialize, add, push, create tag,
    etc.
    """
    path = attr.ib()

    # -------------------------------------------------------------------------
    def status(self):
        """
        Check status of current local git-repository. Returns True if it is
        clean. If there is uncommited stuff it returns False.

        Returns
        -------
        bool
            Represents if current local git-repository is clean.
            If there is uncommited stuff inside the repository, False is
            returned.
        """
        return not bool(
            utils.run_in_bash(f'cd {self.path.absolute()} && git status -s'))

    # -------------------------------------------------------------------------
    def initialize(self):
        """
        Initialize current local project as a git-repository.
        """
        try:
            utils.run_in_bash(f'cd {self.path.absolute()} && git init -q')
        except CalledProcessError:
            inform.error(f'Can\'t initialize git.')

    # -------------------------------------------------------------------------
    def add_all(self):
        """
        Add all content of local git-repository.
        """
        try:
            utils.run_in_bash(f'cd {self.path.absolute()} && git add .')
        except CalledProcessError:
            inform.error(f'Can\'t add files to git folder.')

    # -------------------------------------------------------------------------
    def commit(self):
        """
        Commit current state of local git-repository.
        """
        try:
            utils.run_in_bash(
                f'cd {self.path.absolute()} && '
                f'git ci -m "automatically created by skeleton" -q')
        except CalledProcessError:
            inform.error(f'Can\'t commit files.')

    # -------------------------------------------------------------------------
    def create_tag(self, tag, message):
        """
        Create git tag as passed with passed message for current local
        git-repository.

        Parameters
        ----------
        tag: str
            The tag to create for current local git-repository.
        message: str
            The message to pass with the tag.
        """
        try:
            utils.run_in_bash(f'cd {self.path.absolute()} && '
                              f'git tag -a {tag} -m "{message}"')
        except CalledProcessError:
            inform.error(f'Can\'t create tag {tag}.')

    def get_branch(self):
        try:
            return utils.run_in_bash(f'cd {self.path.absolute()} && '
                                     'git rev-parse --abbrev-ref HEAD')
        except CalledProcessError as err:
            inform.error(f'Can\'t get branch. Got error {err.output}')

    # -------------------------------------------------------------------------
    def get_tag(self):
        """
        Try to get the git tag for the current local git-repository and returns
        the result.
        If the repo doesn't have a git tag yet, it returns "0.0.0"

        Returns
        -------
        str
            Git tag for current local git-repository or "0.0.0" if no git tag
            available yet.
        """
        try:
            return utils.run_in_bash(f'cd {self.path.absolute()} && '
                                     'git describe --tag').split('-')[0]
        except CalledProcessError:
            #inform.error('Project has no git-tag yet.')
            return '0.0.0'

    # -------------------------------------------------------------------------
    def push_tag(self, tag):
        """
        Push passed tag of current local git-repository to its origin.

        Parameters
        ----------
        tag: str
            The tag to push to the git-repositories origin.
        """
        try:
            utils.run_in_bash(f'cd {self.path.absolute()} && '
                              f'git push origin "{tag}"')
        except CalledProcessError:
            inform.error(f'Can\'t push {tag} to origin.')

    # -------------------------------------------------------------------------
    def push_to_branch(self, branch):
        """
        Push passed branch of current local git-repository to its origin.

        Parameters
        ----------
        branch: str
            Branchname to push to origin.
        """
        try:
            utils.run_in_bash(f'cd {self.path.absolute()} && '
                              f'git push -u origin {branch}')
        except CalledProcessError:
            inform.error(f'Can\'t push to branch {branch}.')

    # -------------------------------------------------------------------------
    def set_origin(self, origin):
        """
        Set origin of current local git-repository to passed origin.

        Parameters
        ----------
        origin: str
            Origin to set for the local git-repository.
        """
        try:
            utils.run_in_bash(f'cd {self.path.absolute()} && '
                              f'git remote add origin "{origin}"')
        except CalledProcessError:
            inform.error(f'Can\'t set origin to {origin}.')

    # -------------------------------------------------------------------------
    def get_username(self):
        """
        Collect the name of the current user as defined in the
        .gitconfig-file.

        Returns
        -------
        str
            Name of current user as defined in the .gitconfig-file.
        """
        return utils.run_in_bash('git config user.name')

    # -------------------------------------------------------------------------
    def get_email(self):
        """
        Collect the email of the current user as defined in the
        .gitconfig-file.

        Returns
        -------
        str
            Email of current user as defined in the .gitconfig-file.
        """
        return utils.run_in_bash('git config user.email')

    # -------------------------------------------------------------------------
    def check_tag_on_remote(self):
        """
        Check if current tag is pushed to the origin url.

        Returns
        -------
        check: bool
        """
        try:
            res = utils.run_in_bash(
                f'cd {self.path.absolute()} && '
                f'git ls-remote origin refs/tags/{self.get_tag()}')
            check = bool(res)
        except CalledProcessError as err:
            inform.error(f'Can\'t check if tag exists on remote. '
                         'Following error occured:')
            print(err.output.strip().decode('ascii'))
            check = False
        return check
