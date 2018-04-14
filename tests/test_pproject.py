"""


Description
-----------
   This module contains all pytest-tests for the pproject-package.

"""


import os
from pathlib import Path
import random

from marshmallow import ValidationError
import pytest

from ouroboros.tools.pproject import pproject
from tests.test_config import (testing_project_kwargs,
                               ssh_ok_connection,
                               random_testing_project_kwargs,
                              )


CURRENT_PATH = Path.cwd()


# -----------------------------------------------------------------------------
@pytest.fixture
def cleanup():
    yield
    os.chdir(CURRENT_PATH)


# -----------------------------------------------------------------------------
def created_project(tmpdir):
    os.chdir(tmpdir)
    prj = pproject.Project(path=tmpdir, **testing_project_kwargs)
    prj.update_informations(create=True)
    prj.create()
    path = prj.path
    return path, prj, tmpdir


# -----------------------------------------------------------------------------
def test_project_fails(cleanup, tmpdir):
    os.chdir(tmpdir)
    params = random_testing_project_kwargs()
    params['kwargs']['path'] = tmpdir
    params['kwargs']['project'] = 'bl'
    prj = pproject.Project(**params['kwargs'])
    with pytest.raises(SystemExit):
        prj.create(path=Path(params['kwargs']['path']), on_vcs=True)
    os.chdir(CURRENT_PATH)
    tmpdir.remove()
    os.system(f'rm -rf /var/local/conda/envs/{params["env"]}')


# -----------------------------------------------------------------------------
def test_project_ok(cleanup, tmpdir):
    os.chdir(tmpdir)
    params = random_testing_project_kwargs()
    params['kwargs']['path'] = tmpdir
    prj = pproject.Project(**params['kwargs'])
    prj.create(path=Path(tmpdir), on_vcs=True)
    path = Path(os.path.join(tmpdir, params['env']))
    os.chdir(path)
    prj.update_informations(create=True)
    prj.update()
    prj.test()
    prj.new_version(vtype='major')
    prj.new_version(vtype='minor')
    prj.new_version(vtype='patch')
    prj.info()
    pproject.general_info()
    prj.build()
    prj.release(dst='localhost')
    prj.release(dst=ssh_ok_connection)
    prj.sphinx()
    os.chdir(CURRENT_PATH)
    tmpdir.remove()
    os.system(f'rm -rf /var/local/conda/envs/{params["env"]}')


# =============================================================================
class TestProject:
    # -------------------------------------------------------------------------
    def test_project_build_fails(self, cleanup, tmpdir):
        path, prj, tdir = created_project(tmpdir)
        os.chdir(path)
        (Path(path) / 'testfile.py').touch()
        with pytest.raises(SystemExit):
            prj.build()
        tdir.remove()

    # -------------------------------------------------------------------------
    def test_project_new_version_fails(self, cleanup, tmpdir):
        path, prj, tdir = created_project(tmpdir)
        os.chdir(path)
        with pytest.raises(AssertionError):
            prj.new_version(vtype='bug', path=path)
        tdir.remove()


    # -------------------------------------------------------------------------
    def test_project_new_version_after_change_fails(self, cleanup, tmpdir):
        path, prj, tdir = created_project(tmpdir)
        os.chdir(path)
        (Path(path) / 'testfile.py').touch()
        with pytest.raises(SystemExit):
            prj.new_version(vtype='major', path=path)
        tdir.remove()

    # -------------------------------------------------------------------------
    def test_project_info_no_pproject_project_ok(self, cleanup):
        os.chdir('/home')
        pproject.general_info()

    # -------------------------------------------------------------------------
    def test_create_already_exists_fails(self, cleanup, tmpdir):
        os.chdir(tmpdir)
        params = random_testing_project_kwargs()
        prj = pproject.Project(path=tmpdir, **params['kwargs'])
        prj.update_informations(create=True)
        prj.create()
        os.chdir(tmpdir)
        with pytest.raises(SystemExit):
            prj.create()
        tmpdir.remove()
        os.system(f'rm -rf /var/local/conda/envs/{params["env"]}')


# =============================================================================
class TestBuildArguments:
    # -------------------------------------------------------------------------
    def test_build_arguments_info_ok(self, cleanup):
        info_parser = pproject.build_arguments(['info'])
        assert info_parser.tool == 'info'

    # -------------------------------------------------------------------------
    def test_build_arguments_create_modules_ok(self, cleanup):
        create_modules_parser = pproject.build_arguments(
            ['create',
             'testing',
             '-n',
             'testing'])
        assert create_modules_parser.tool == 'create'
        assert not create_modules_parser.remote
        assert create_modules_parser.namespace == 'testing'
        assert create_modules_parser.projectname == 'testing'
        assert create_modules_parser.pythonversion == '3.6'


# =============================================================================
class TestRun:
    # -------------------------------------------------------------------------
    def test_run_info(self, tmpdir):
        path, prj, tdir = created_project(tmpdir)
        os.chdir(path)
        options = pproject.build_arguments(['info', 'project'])
        pproject.run(options)
        options = pproject.build_arguments(['info', 'general'])
        pproject.run(options)

    # -------------------------------------------------------------------------
    def test_run_create_update_test_version_build(self, cleanup, tmpdir):
        os.chdir(tmpdir)
        nbr = random.randint(1, 100000)
        for args in (['create', '--remote', 'testing', '-n', f'testing{nbr}'],
                     ['info', 'general'],
                     ['info', 'project'],
                     ['update'],
                     ['test'],
                     ['version', '-m', 'blub', 'major'],
                     ['build'],
                     ['sphinx']):
            os.chdir(tmpdir)
            directory = Path(tmpdir)
            if args[0] != 'create':
                prjname = f'ouroboros-testing-testing{nbr}'
                os.chdir(str(Path(tmpdir) / prjname))
                directory = Path(tmpdir) / prjname
            pproject.run(
                options=pproject.build_arguments(args),
                path=Path(tmpdir))
            os.system(f'rm -rf /var/local/conda/envs/testing{nbr}')
