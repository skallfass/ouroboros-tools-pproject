import os
from pathlib import Path
import random

import pytest

from ouroboros.tools.pproject import sphinx
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


# -----------------------------------------------------------------------------
def test_sphinx_docu_ok(cleanup, tmpdir):
    path, prj, tdir = created_project(tmpdir)
    os.chdir(path)
    sphinx.run_sphinx_quickstart(path=Path(path),
                                 environment=prj.environment,
                                 username='dummyuser',
                                 version='0.0.1')
    sphinx.customize_config(path=Path(path))
    sphinx.create_coverage_badge(path=Path(path), environment=prj.environment)
    sphinx.update_source(path=Path(path))
    sphinx.make_documentation(path=Path(path))
    assert (Path(path) / 'source').exists()
    assert (Path(path) / 'build').exists()


# -----------------------------------------------------------------------------
def test_sphinx_make_documentation_fails(tmpdir):
    os.chdir(tmpdir)
    sphinx.make_documentation(path=Path(tmpdir))
