"""


Description
-----------
   This module contains all pytest-tests for the pproject-package.

"""


import os
from subprocess import CalledProcessError
from pathlib import Path
import pytest
from ouroboros.tools.pproject import utils
from tests.test_config import (ssh_ok_connection,
                               ssh_fail_connections,
                               testconfig_path)


CURRENT_PATH = Path.cwd()


# =============================================================================
class TestMD5:
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize('fname', [
        Path('tests/md5_testfile.txt').absolute(),
        Path('tests/md5_testfile.txt'),
        str(Path('tests/md5_testfile.txt').absolute()),
        str(Path('tests/md5_testfile.txt'))])
    def test_md5_ok(self, fname):
        """
        Testfunction to check if pproject.md5-function calculates the md5sum correctly.
        """
        os.chdir(CURRENT_PATH)
        assert utils.md5(fname) == '0f1c139fc35d4154f0bbafacd3de2189'

    # -------------------------------------------------------------------------
    @pytest.mark.parametrize('fname',
                             [1,
                              2.0,
                              {},
                              [],
                              (),
                              ('tests/md5_testfile.txt',),
                              {'fname': 'tests/md5_testfile.txt'},
                              'md5_testfile.txt',
                              None,
                             ])
    def test_md5_fails(self, fname):
        """
        Testfunction to check if oc.md5-function correctly fails with wrong input.
        """
        with pytest.raises(AssertionError):
            utils.md5(fname)


# =============================================================================
class TestRunInBash:
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize('command', ['echo "hello"',])
    def test_run_in_bash_ok(self, command):
        assert utils.run_in_bash(command) == 'hello'

    # -------------------------------------------------------------------------
    @pytest.mark.parametrize('command', ['umdibumdi',])
    def test_run_in_bash_fails(self, command):
        with pytest.raises(CalledProcessError):
            utils.run_in_bash(command)


# =============================================================================
class TestConnectSSH:
    # -------------------------------------------------------------------------
    def test_connect_ssh_ok(self):
        utils.connect_ssh(ssh_ok_connection)

    # -------------------------------------------------------------------------
    @pytest.mark.parametrize('userathost', ssh_fail_connections)
    def test_connect_ssh_fails(self, userathost):
        with pytest.raises(SystemExit):
            utils.connect_ssh(userathost)


# =============================================================================
class TestConfig:
    # -------------------------------------------------------------------------
    def test_load_configs_ok(self):
        utils.load_configs(user_config_path=Path(testconfig_path).absolute())

    # -------------------------------------------------------------------------
    def test_get_config_ok(self, capsys):
        utils.get_config_for_terminal()
        captured = capsys.readouterr()
        assert captured[0] == (
            'conda_folder=/var/local/conda\n'
            'meta_yaml_path=conda-build/meta.yaml\n'
            'meta_yaml_md5_path=conda-build/hash.md5\n'
            'pproject_env=/var/local/conda/envs/pproject\n'
            'skeleton_repo=git@gitlab.com:skallfass-ouroboros/skeleton.git\n'
            'company=ouroboros\n'
            )
