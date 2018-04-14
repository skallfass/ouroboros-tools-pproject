# -*- coding: utf-8 -*-

"""
Copyright (C) 2018 Simon Kallfass

sphinx-commands used by the pproject-module.
"""

from subprocess import CalledProcessError

from ouroboros.tools.pproject import inform
from ouroboros.tools.pproject import utils


CONFIG = utils.load_configs()
PPROJECT_ENV_PATH = CONFIG['pproject_env']
"""str: The folder where the pproject-env is stored."""
COMPANY = CONFIG['company']
"""str: The company name to use for new project creations based on
"pproject create"."""
SPHINX_QUICKSTART = f'{PPROJECT_ENV_PATH}/bin/sphinx-quickstart'
PYTEST = f'{PPROJECT_ENV_PATH}/bin/pytest'
COVERAGE_BADGE = f'{PPROJECT_ENV_PATH}/bin/coverage-badge'
SPHINX_APIDOC = f'{PPROJECT_ENV_PATH}/bin/sphinx-apidoc'
SPHINXBUILD = f'{PPROJECT_ENV_PATH}/bin/sphinx-build'


# -----------------------------------------------------------------------------
def run_sphinx_quickstart(path, environment, username, version):
    """
    Run sphinx-quickstart for the passed path. Required variables for this
    setup are the passed environment (as name of the project), the username
    and the version of the project to document.

    Parameters
    ----------
    path: pathlib.Path
        Path to create the documentation for.
    environment: str
        The name of the project to document.
    username: str
        The name of maintainer of the project.
    version: str
        The current version of the project.
    """
    inform.info('Running sphinx-quickstart')
    utils.run_in_bash(f"cd {path.absolute()} && "
                      f"{SPHINX_QUICKSTART} "
                      "-q "
                      f"-p '{environment}' "
                      f"-a '{username}' "
                      f"-v {version} "
                      "-l en "
                      "--ext-autodoc --ext-todo --ext-coverage "
                      "--ext-viewcode "
                      "--extensions=sphinx.ext.napoleon "
                      "--makefile --sep")


# -----------------------------------------------------------------------------
def customize_config(path):
    """
    Rename content of source/conf.py for custom setup.

    Parameters
    ----------
    path: pathlib.Path
        Path to create the documentation for.
    """
    inform.info('Renaming content of source/conf.py for custom setup')
    find_replace = {
        '# import os': 'import os',
        '# import sys': 'import sys',
        "# sys.path.insert(0, os.path.abspath('.'))": (
            "sys.path.insert(0, os.path.abspath('..'))"),
        "html_theme = 'alabaster'": (
            "html_theme = 'sphinx_rtd_theme'"),
        "        'relations.html',": "",
        "        'searchbox.html',": ("['globaltoc.html', "
                                      "'localtoc.html', "
                                      "'relations.html', "
                                      "'sourcelink.html', "
                                      "'searchbox.html'],")}

    with open(str(path / "source/new_data.txt"), 'w') as new_data:
        with open(str(path / 'source/conf.py'), 'r') as data:
            for line in data:
                for key in find_replace:
                    if key in line:
                        line = line.replace(key, find_replace[key])
                new_data.write(line)
    utils.run_in_bash(f'mv {str((path / "source/new_data.txt").absolute())} '
                      f'{str((path / "source/conf.py").absolute())}')


# -----------------------------------------------------------------------------
def create_coverage_badge(path, environment):
    """
    Run pytest-cov and create coverage-badge for the coverage-result.
    Store the resulting badge inside the static folder for use inside
    documentation.

    Parameters
    ----------
    path: pathlib.Path
        Path where to change into for testing and creation of badge.
    environment: str
        Name of the project to document.
    """
    inform.info('Running pytest-cov and creating coverage-badge')
    try:
        utils.run_in_bash(
            f'cd {str(path.absolute())} && '
            f'{PYTEST} --cov={COMPANY} --cov-report term-missing -v && '
            f'{COVERAGE_BADGE} -o source/_static/{environment}_coverage.svg -f')
    except CalledProcessError as err:
        print(err.output.strip().decode('ascii'))


# -----------------------------------------------------------------------------
def update_source(path):
    """
    Update source for documentation to create of passed path.

    Parameters
    ----------
    path: pathlib.Path
        Path to create the documentation for.
    """
    inform.info('Updating source for documentation to create')
    try:
        utils.run_in_bash(
            f'cd {str(path.absolute())} && '
            f'{SPHINX_APIDOC} -f -o source/ .')
    except CalledProcessError as err:
        print(err.output.strip().decode('ascii'))


# -----------------------------------------------------------------------------
def make_documentation(path):
    """
    Generatie html- and pdf-documentation for passed path.

    Parameters
    ----------
    path: pathlib.Path
        Path to create the documentation for.
    """
    inform.info('Generating html- and pdf-documentation')
    try:
        utils.run_in_bash(
            f'cd {str(path.absolute())} && '
            f'make SPHINXBUILD={SPHINXBUILD} html')
    except CalledProcessError as err:
        print(err.output.strip().decode('ascii'))
