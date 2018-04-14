"""


Description
-----------
   This module contains all pytest-tests for the pproject-package.

"""


import os
from subprocess import CalledProcessError
from pathlib import Path
import pytest
from ouroboros.tools.pproject import inform


CURRENT_PATH = Path.cwd()


# -----------------------------------------------------------------------------
def test_inform_info(capsys):
    inform.info('bla')
    captured = capsys.readouterr()
    assert captured[0] == b' \x1b[1;37m\xe2\x84\xb9\x1b[0m\x1b[0;94m     TEST_INFORM_INFO \x1b[0mbla\n'.decode('utf8')


# -----------------------------------------------------------------------------
def test_inform_error(capsys):
    inform.error('bla')
    captured = capsys.readouterr()
    assert captured[0] == b' \x1b[1;91mE\x1b[0m\x1b[0;94m    TEST_INFORM_ERROR \x1b[0mbla\n'.decode('utf8')


# -----------------------------------------------------------------------------
def test_inform_critical(capsys):
    with pytest.raises(SystemExit):
        inform.critical('bla')
    captured = capsys.readouterr()
    assert captured[0] == b' \x1b[1;91m\xe2\x9c\x98\x1b[0m\x1b[0;94m  TEST_INFORM_CRITICAL \x1b[0mbla\n'.decode('utf8')
