import os
from pathlib import Path

import pytest

from ouroboros.tools.pproject import conda
from tests.test_config import correct_myaml_content


CURRENT_PATH = Path.cwd()


# =============================================================================
class TestMetaYaml:
    # -------------------------------------------------------------------------
    def test_metayaml_ok(self):
        os.chdir(CURRENT_PATH)
        conda.MetaYaml(path=Path('conda-build/meta.yaml').absolute())

    # -------------------------------------------------------------------------
    def test_metayaml_fail(self):
        os.chdir(CURRENT_PATH)
        with pytest.raises(AttributeError):
            conda.MetaYaml(path=Path('/tmp/conda-build/meta.yaml'))

    # -------------------------------------------------------------------------
    def test_metayaml_update_ok(self):
        os.chdir(CURRENT_PATH)
        myaml = conda.MetaYaml(path=Path('conda-build/meta.yaml').absolute())
        myaml.update()

    # -------------------------------------------------------------------------
    def test_metayaml_get_content_ok(self):
        os.chdir(CURRENT_PATH)
        myaml = conda.MetaYaml(path=Path('conda-build/meta.yaml').absolute())
        myaml_content = myaml.get_content()
        assert myaml_content == correct_myaml_content


# -----------------------------------------------------------------------------
def test_condaenvironment_ok():
    condaenv = conda.CondaEnvironment(name='pproject_testing_env')
    assert not condaenv.exists()
    condaenv.create(dependencies=['python=3.6', 'attrs=17.3'])
    condaenv.recreate(dependencies=['python=3.6', 'attrs=17.3'])
    condaenv.remove()
