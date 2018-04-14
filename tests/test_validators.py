"""


Description
-----------
   This module contains all pytest-tests for the pproject-package.

"""


import os
from subprocess import CalledProcessError
import logging
from pathlib import Path
import random
import pytest
from marshmallow import ValidationError
from ouroboros.tools.pproject import validators


CURRENT_PATH = Path.cwd()


# -----------------------------------------------------------------------------
def test_validate_environmentname_ok():
    validators.validate_environmentname(
            environment='ouroboros-testing-project')


# -----------------------------------------------------------------------------
@pytest.mark.parametrize('environment', [
    'ouroboros-testing',
    ])
def test_validate_environmentname_fails(environment):
    with pytest.raises(ValidationError):
        validators.validate_environmentname(environment=environment)


# -----------------------------------------------------------------------------
def test_validate_version_ok():
    validators.validate_version(version='1.0.0')


# -----------------------------------------------------------------------------
@pytest.mark.parametrize('version', [
    '1.0',
    '1.0.0.0',
    '1.e.0',
    ])
def test_validate_version_fails(version):
    with pytest.raises(ValidationError):
        validators.validate_version(version=version)


# -----------------------------------------------------------------------------
def test_validate_path_exists_ok():
    validators.validate_path_exists(path='/tmp')


# -----------------------------------------------------------------------------
def test_validate_path_exists_fails():
    with pytest.raises(ValidationError):
        validators.validate_path_exists(path='/tmp/aaaaaaabbbbbccccc010101010')


# -----------------------------------------------------------------------------
def test_validate_url_ok():
    validators.validate_url(url='https://google.de')


# -----------------------------------------------------------------------------
@pytest.mark.parametrize('url', [
    'umdibumdi',
    'http://httpstat.us/500',
    'http://httpstat.us/400',
    ])
def test_validate_url_fails(url):
    with pytest.raises(ValidationError):
        validators.validate_url(url=url)


# -----------------------------------------------------------------------------
def test_validate_SConfig_ok():
    params = dict(conda_folder='/var/local/conda',
                  meta_yaml_path='test',
                  meta_yaml_md5_path='test',
                  environment_yaml_path='test',
                  pproject_env='/var/local/conda/bin/conda',
                  skeleton_repo='test',
                  company='test',
                  gitlab_url='http://gitlab.com',
                  gitlab_api='test',
                  gitlab_token_path='/tmp',
                  gitlab_ssh='test',
                  conda_repo_userathost='bla@blub',
                  conda_repo_pkgs_path='/var/local/conda/conda-bld/linux-64',
                  conda_repo_conda_bin='/var/local/conda/bin/conda',
                  pytest_arguments=['--cache', '-r'])
    validators.SConfig(strict=True).load(params)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize('attribute, value', [
    ('conda_folder', 'blub'),
    ('conda_folder', None),
    ('conda_folder', 1),
    ('conda_folder', 1.2),
    ('conda_folder', []),
    ('conda_folder', {}),
    ('meta_yaml_path', None),
    ('meta_yaml_path', 1),
    ('meta_yaml_path', 1.2),
    ('meta_yaml_path', []),
    ('meta_yaml_path', {}),
    ('meta_yaml_md5_path', None),
    ('environment_yaml_path', None),
    ('pproject_env', None),
    ('skeleton_repo', None),
    ('company', None),
    ('company', 'ha'),
    ('gitlab_url', 'bla'),
    ('gitlab_url', 'http://httpstat.us/500'),
    ('gitlab_url', None),
    ('gitlab_api', None),
    ('gitlab_token_path', None),
    ('gitlab_ssh', None),
    ('conda_repo_userathost', None),
    ('conda_repo_pkgs_path', None),
    ('conda_repo_conda_bin', None),
    ('pytest_arguments', None),
    ('pytest_arguments', 1),
    ('pytest_arguments', 1.2),
    ('pytest_arguments', 'bla'),
    ('pytest_arguments', {}),
    ('pytest_arguments', [1, 'blub']),
    ])
def test_validate_SConfig_fails(attribute, value):
    params = dict(conda_folder='/var/local/conda',
                  meta_yaml_path='test',
                  meta_yaml_md5_path='test',
                  environment_yaml_path='test',
                  pproject_env='/var/local/conda/bin/conda',
                  skeleton_repo='test',
                  company='test',
                  gitlab_url='http://gitlab.com',
                  gitlab_api='test',
                  gitlab_token_path='/tmp',
                  gitlab_ssh='test',
                  conda_repo_userathost='bla@blub',
                  conda_repo_pkgs_path='/var/local/conda/conda-bld/linux-64',
                  conda_repo_conda_bin='/var/local/conda/bin/conda',
                  pytest_arguments=['--cache', '-r'])
    params[attribute] = value
    with pytest.raises(ValidationError):
        validators.SConfig(strict=True).load(params)


# -----------------------------------------------------------------------------
def test_validate_SProject_ok():
    params = dict(company='ouroboros',
                  namespace='testing',
                  project='test',
                  pythonversion='3.6',
                  username='Dummy User',
                  email='dummy@user.com',
                  year='2017-01-01',
                  today='2017-01-01T00:00:00+00:00',
                  version='1.0.0',
                  environment='ouroboros-testing-test')
    validators.SProject(strict=True).load(params)


# -----------------------------------------------------------------------------
@pytest.mark.parametrize('attribute, value', [
    ('company', 'bl'),
    ('company', None),
    ('company', 1),
    ('company', 1.2),
    ('company', []),
    ('company', {}),
    ('namespace', 'bl'),
    ('project', 'bl'),
    ('pythonversion', 1.2),
    ('pythonversion', 1),
    ('pythonversion', None),
    ('pythonversion', []),
    ('pythonversion', {}),
    ('pythonversion', 3.6),
    ('pythonversion', 2.7),
    ('pythonversion', '2.6'),
    ('username', None),
    ('email', None),
    ('year', None),
    ('today', None),
    ('version', '1.0'),
    ('version', '1.0.0.0'),
    ('version', '1.e.0'),
    ('environment', None),
    ('environment', 'ouroboros-testing'),
    ('environment', 'ouroboros-ts-test'),
    ])
def test_validate_SProject_fails(attribute, value):
    params = dict(company='ouroboros',
                  namespace='testing',
                  project='test',
                  pythonversion='3.6',
                  username='Dummy User',
                  email='dummy@user.com',
                  year='2017-01-01',
                  today='2017-01-01T00:00:00+00:00',
                  version='1.0.0',
                  environment='ouroboros-testing-test')
    params[attribute] = value
    with pytest.raises(ValidationError):
        validators.SProject(strict=True).load(params)


# -----------------------------------------------------------------------------
def test_validate_SPackage_ok():
    params = dict(name='ouroboros',
                  version='1.0.0')
    validators.SPackage(strict=True).load(params)


# -----------------------------------------------------------------------------
def test_validate_SSource_ok():
    params = dict(path='..')
    validators.SSource(strict=True).load(params)


# -----------------------------------------------------------------------------
def test_validate_SBuild_ok():
    params = dict(build='python setup.py etc.',
                  preserve_egg_dir=True,
                  entry_points=['first', 'second'])
    validators.SBuild(strict=True).load(params)


# -----------------------------------------------------------------------------
def test_validate_SRequirements_ok():
    params = dict(build=['python'],
                  run=['python'])
    validators.SRequirements(strict=True).load(params)


# -----------------------------------------------------------------------------
def test_validate_STest_ok():
    params = dict(imports=['pytest'],
                  commands=['pytest --help'])
    validators.STest(strict=True).load(params)


# -----------------------------------------------------------------------------
def test_validate_SExtra_ok():
    params = dict(maintainer='Dummy User',
                  pythonversion='3.6')
    validators.SExtra(strict=True).load(params)


# -----------------------------------------------------------------------------
def test_validate_SMetaYaml_ok():
    params = dict(package=dict(name='ouroboros', version='1.0.0'),
                  source=dict(path='..'),
                  build=dict(build='python setup.py etc.',
                             preserve_egg_dir=True,
                             entry_points=['first', 'second']),
                  requirements=dict(build=['python'], run=['python']),
                  test=dict(imports=['pytest'],
                            commands=['pytest --help']),
                  about={},
                  extra=dict(maintainer='Dummy User', pythonversion='3.6'))
    validators.SMetaYaml(strict=True).load(params)
