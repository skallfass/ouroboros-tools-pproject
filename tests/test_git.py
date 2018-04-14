import os
from pathlib import Path
import random

import pytest

from ouroboros.tools.pproject import git
from ouroboros.tools.pproject import pproject
from tests.test_config import testing_project_kwargs

CURRENT_PATH = Path.cwd()


# -----------------------------------------------------------------------------
def created_project(tmpdir):
    os.chdir(tmpdir)
    prj = pproject.Project(path=tmpdir, **testing_project_kwargs)
    prj.update_informations(create=True)
    prj.create()
    path = prj.path
    return path, prj, tmpdir


# -----------------------------------------------------------------------------
@pytest.fixture
def cleanup():
    yield
    os.chdir(CURRENT_PATH)


# =============================================================================
class TestGitAndVCS:
    # -------------------------------------------------------------------------
    def test_get_vcs_token_ok(self):
        gtoken = git.get_vcs_token()
        assert isinstance(gtoken, str)
        assert gtoken

    # -------------------------------------------------------------------------
    def test_get_gitlab_groups_ok(self):
        res = git.get_gitlab_groups()
        assert res != {}

    # -------------------------------------------------------------------------
    def test_check_remote_vcs_ok(self):
        assert git.check_remote_vcs()

    # -------------------------------------------------------------------------
    def test_create_on_vcs_ok(self, tmpdir):
        curr_git = git.GitRepo(path=Path(tmpdir))
        git.create_on_remote_vcs(
            company='ouroboros',
            namespace='testing',
            project=f'pytesttesting{random.randint(1, 100000)}',
            username=curr_git.get_username())


# -----------------------------------------------------------------------------
def test_gitrepo_ok(cleanup, tmpdir):
    path, prj, tdir = created_project(tmpdir)
    os.chdir(path)
    prj.new_version(vtype='major')
    curr_git = git.GitRepo(path=path)
    assert curr_git.get_tag() == '1.0.0'
    (Path(path) / 'testfile.txt').touch()
    assert not curr_git.status()
    curr_git.add_all()
    curr_git.commit()
    assert curr_git.status()
    curr_git.create_tag(tag='20.0.0', message='bla')
    assert curr_git.get_tag() == '20.0.0'
    assert curr_git.get_username()
    assert curr_git.get_email()
    tdir.remove()


# -----------------------------------------------------------------------------
def test_gitrepo_initialize_ok(cleanup, tmpdir):
    os.chdir(tmpdir)
    curr_git = git.GitRepo(path=Path(tmpdir))
    curr_git.initialize()
    assert curr_git.status()
    (Path(tmpdir) / 'testfile.txt').touch()
    assert not curr_git.status()
