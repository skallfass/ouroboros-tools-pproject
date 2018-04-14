# -*- coding: utf-8 -*-

"""
Copyright (C) 2018 Simon Kallfass

Provides validators used in the pproject-module (project-, config- and
meta.yaml-validations).
"""


from pathlib import Path
import urllib.request

from marshmallow import fields, Schema, ValidationError, validate
import toastedmarshmallow


# ------------------------------------------------------------------- VALIDATOR
def validate_environmentname(environment):
    """
    Validates if the passed environment is valid.

    Parameters
    ----------
    environment: str
        The environment-name to validate.

    Raises
    ------
    marshmallow.ValidationError
        If environment isn't valid, raises a marshmallow.ValidationError.
    """
    environment_splitted = environment.split('-')
    for val in environment_splitted:
        if len(val) < 3:
            raise ValidationError(
                f'Environment {environment} is not valid. Each part of '
                'company-namespace-project naming style must have minimal '
                'length of 3.')
    if not len(environment_splitted) == 3:
        raise ValidationError(
            f'Environment {environment} is not valid. Not in '
            'company-namespace-project naming style.')


# ------------------------------------------------------------------- VALIDATOR
def validate_version(version):
    """
    Validates if the passed version is valid
    (form and semantic-versioning-style).

    Parameters
    ----------
    version: str
        The version to validate.

    Raises
    ------
    marshmallow.ValidationError
        If version isn't valid, raises a marshmallow.ValidationError.
    """
    version_splitted = version.split('.')
    if version:
        for val in version_splitted:
            try:
                int(val)
            except:
                raise ValidationError(
                    f'Version {version} is not valid. Not in semantic versioning '
                    'style.')
        if not len(version_splitted) == 3:
            raise ValidationError(
                f'Version {version} is not valid. Not in semantic versioning '
                'style.')


# ------------------------------------------------------------------- VALIDATOR
def validate_path_exists(path):
    """
    Validates if the passed path exists.

    Parameters
    ----------
    path: str
        The path to check.

    Raises
    ------
    marshmallow.ValidationError
        If path doesn't exist, raises a marshmallow.ValidationError.
    """
    if '~' in path:
        path = path.replace('~', str(Path.home().absolute()))
    if not Path(path).exists():
        raise ValidationError(f'Path {path} doesn\'t exist.')


# ------------------------------------------------------------------- VALIDATOR
def validate_url(url):
    """
    Validates if the passed url is valid.

    Parameters
    ----------
    url: str
        The url to validate.

    Raises
    ------
    marshmallow.ValidationError
        If passed url isn't valid, raises a marshmallow.ValidationError.
    """
    try:
        status = urllib.request.urlopen(url).getcode()
    except:
        raise ValidationError(f'Passed url {url} can\'t be reached.')
    if status != 200:
        raise ValidationError(
            f'Passed url {url} can\'t be reached (Http-code: {status}).')


# ====================================================================== SCHEMA
class SToasted(Schema):
    """
    The base-Schema-class to use for all other schemata in this module.
    Using toastedmarshmallow.Jit speeds up validation.
    """
    class Meta:
        """
        Meta-class used to speed up marshmallow-validation.
        """
        jit = toastedmarshmallow.Jit


# ====================================================================== SCHEMA
# TODO: make dynamic with CONFIG['used_vcs']
class SConfig(SToasted):
    """
    The schema-class for the pproject-config.

    Attributes
    ----------
    conda_folder: str
    meta_yaml_path: str
    meta_yaml_md5_path: str
    environment_yaml_path: str
    pproject_env: str
    skeleton_repo: str
    company: str
    gitlab_url: str
    gitlab_api: str
    gitlab_token_path: str
    gitlab_ssh: str
    conda_repo_userathost: str
    conda_repo_pkgs_path: str
    conda_repo_conda_bin: str
    pytest_arguments: list
    """
    conda_folder = fields.String(strict=True, validate=validate_path_exists)
    meta_yaml_path = fields.String(strict=True)
    meta_yaml_md5_path = fields.String(strict=True)
    environment_yaml_path = fields.String(strict=True)
    pproject_env = fields.String(strict=True)
    skeleton_repo = fields.String(strict=True)
    company = fields.String(strict=True,
                            validate=validate.Length(min=3))
    gitlab_url = fields.String(strict=True, validate=[validate_url,
                                                      validate.URL])
    gitlab_api = fields.String(strict=True)
    gitlab_token_path = fields.String(strict=True,
                                      validate=validate_path_exists)
    gitlab_ssh = fields.String(strict=True)
    conda_repo_userathost = fields.String(strict=True)
    conda_repo_pkgs_path = fields.String(strict=True)
    conda_repo_conda_bin = fields.String(strict=True)
    pytest_arguments = fields.List(fields.String(strict=True), strict=True)


# ====================================================================== SCHEMA
class SProject(SToasted):
    """
    The schema-class for pproject-projects.

    Attributes
    ----------
    company: str
    namespace: str
    project: str
    pythonversion: str
    username: str
    email: str
    year: str
    today: str
    version: str
    environment: str
    """
    company = fields.String(strict=True,
                            required=True,
                            validate=validate.Length(min=3))
    namespace = fields.String(strict=True,
                              required=True,
                              validate=validate.Length(min=3))
    project = fields.String(strict=True,
                            required=True,
                            validate=validate.Length(min=3))
    pythonversion = fields.String(strict=True,
                                  required=True,
                                  validate=validate.OneOf(['2.7', '3.6']))
    username = fields.String(strict=True, required=True)
    email = fields.String(strict=True, required=True, validate=validate.Email)
    year = fields.String(strict=True, required=True)
    today = fields.String(strict=True, required=True)
    version = fields.String(strict=True,
                            required=True,
                            validate=validate_version,
                            allow_none=True)
    environment = fields.String(strict=True,
                                required=True,
                                validate=validate_environmentname)


# ====================================================================== SCHEMA
class SPackage(SToasted):
    """
    The schema-class for the package-section used as nested-field in SMetaYaml.

    Attributes
    ----------
    name: str
    version: str
    """
    name = fields.String(strict=True, required=True)
    version = fields.String(strict=True, allow_none=True, required=True)


# ====================================================================== SCHEMA
class SSource(SToasted):
    """
    The schema-class for the source-section used as nested-field in SMetaYaml.

    Attributes
    ----------
    path: str
    """
    path = fields.String(strict=True, required=True)


# ====================================================================== SCHEMA
class SBuild(SToasted):
    """
    The schema-class for the build-section used as nested-field in SMetaYaml.

    Attributes
    ----------
    build: str
    preserve_egg_dir: bool
    entry_points: list
    """
    build = fields.String(strict=True, required=True, allow_none=True)
    preserve_egg_dir = fields.Boolean(strict=True, required=True)
    entry_points = fields.List(fields.String(strict=True, required=True),
                               strict=True, allow_none=True)


# ====================================================================== SCHEMA
class SRequirements(SToasted):
    """
    The schema-class for the requirements-section used as nested-field in
    SMetaYaml.

    Attributes
    ----------
    build: list
    run: list
    """
    build = fields.List(fields.String(strict=True, required=True),
                        strict=True, required=True)
    run = fields.List(fields.String(strict=True, required=True),
                      strict=True, required=True)


# ====================================================================== SCHEMA
class STest(SToasted):
    """
    The schema-class for the test-section used as nested-field in SMetaYaml.

    Attributes
    ----------
    imports: list
    commands: list
    """
    imports = fields.List(fields.String(strict=True, required=True),
                          strict=True, required=True)
    commands = fields.List(fields.String(strict=True, required=True),
                           strict=True, required=True, allow_none=True)


# ====================================================================== SCHEMA
class SExtra(SToasted):
    """
    The schema-class for the extra-section used as nested-field in SMetaYaml.

    Attributes
    ----------
    maintainer: str
    pythonversion: str
    """
    maintainer = fields.String(strict=True, required=True)
    pythonversion = fields.String(strict=True, required=True,
                                  validate=validate.OneOf(['2.7', '3.6']))


# ====================================================================== SCHEMA
class SMetaYaml(SToasted):
    """
    The schema-class to use for meta.yaml-contents used in pproject.

    Attributes
    ----------
    package: marshmallow.fields.Nested
    source: marshmallow.fields.Nested
    build: marshmallow.fields.Nested
    requirements: marshmallow.fields.Nested
    test: marshmallow.fields.Nested
    about: dict
    extra: marshmallow.fields.Nested
    """
    package = fields.Nested(SPackage, strict=True, required=True)
    source = fields.Nested(SSource, strict=True, required=True)
    build = fields.Nested(SBuild, strict=True, required=True)
    requirements = fields.Nested(SRequirements, strict=True, required=True)
    test = fields.Dict(strict=True, required=True)
    about = fields.Dict(strict=True, allow_none=True)
    extra = fields.Nested(SExtra, strict=True, required=True)
