from pathlib import Path
import random

company = 'ouroboros'

gitlab_url = 'http://127.0.0.1:80'

gitlab_ssh = 'ssh://git@localhost:50000'

gitlab_api = 'http://127.0.0.1:80/api/v4'

gitlab_token = 'wyb9QSqYbzMoKqtA5BUv'

publish_kwargs = dict(
    destination='skall@biela.uberspace.de',
    sourcepath='/var/local/conda/conda-bld/linux-64/aiohttp-2.2.5-py36_0.tar.bz2',
    destinationpath='/var/www/virtual/skall/html/conda_pkgs/linux-64',
    destination_conda_bin='/home/skall/miniconda3/bin/conda')

testing_project_kwargs = dict(company='ouroboros',
                              namespace='testing',
                              project='testing',
                              pythonversion='3.6')

testing_project_name = (f'{testing_project_kwargs["company"]}-'
                        f'{testing_project_kwargs["namespace"]}-'
                        f'{testing_project_kwargs["project"]}')

ssh_ok_connection = 'ektom@gallifrey'

ssh_fail_connections = ['bla@gallifrey', 'root@gallifrey', 'bla@blub']

testconfig_path = 'tests/ocp_config.yml'

correct_myaml_content = {
    'package': {'name': 'ouroboros-tools-pproject', 'version': 'None'},
    'source': {'path': '..'},
    'build': {'build': '0',
              'preserve_egg_dir': 'True',
              'entry_points': [
                  'pproject_py = ouroboros.tools.pproject.pproject:main',
                  'pproject_read_config = ouroboros.tools.pproject.utils:get_config_for_terminal']},
    'requirements': {'build': ['python 3.6.3',
                               'setuptools'],
                     'run': ['python 3.6.3',
                             'attrs >=17.4*',
                             'cookiecutter >=1.5*',
                             'ipython',
                             'jinja2',
                             'marshmallow',
                             'paramiko >=2.4*',
                             'pylint >=1.8.2*',
                             'pytest 3.3.1',
                             'pytest-cov >=2.5*',
                             'pytest-lazy-fixture >=0.4*',
                             'pytest-xdist >=1.22*',
                             'pyyaml',
                             'ruamel.yaml',
                             'sphinx >=1.7*',
                             'toastedmarshmallow',
                             'coverage >=4.5*',
                             'coverage-badge',
                             'sphinx_rtd_theme',
                             'sphinx_bootstrap_theme',
                            ]},
    'test': {'imports': ['ouroboros.tools.pproject.pproject',
                         'ouroboros.tools.pproject.utils',
                         'ouroboros.tools.pproject.validators',
                         'ouroboros.tools.pproject.conda',
                         'ouroboros.tools.pproject.git',
                         'ouroboros.tools.pproject.inform',
                         ],
             'commands': ['pproject_py --help', 'pproject_read_config']},
    'about': {'license': 'GNU GPLv3.0', 'license_file': 'LICENSE'},
    'extra': {'maintainer': 'Simon Kallfass', 'pythonversion': '3.6'}}


# -----------------------------------------------------------------------------
def gitlab_token_path(CURRENT_PATH):
    return str((Path(CURRENT_PATH) / 'tests/testtoken').absolute())


# -----------------------------------------------------------------------------
def release_ok_attrs():
    return dict(envname=f'release_local_test{random.randint(1, 100000)}',
                pyversion='2.7',
                packagename='attrs',
                version='17.4.0')


# -----------------------------------------------------------------------------
def release_remote_ok_attrs():
    kwargs = release_ok_attrs()
    kwargs.update(dict(dst=ssh_ok_connection))
    return kwargs


# -----------------------------------------------------------------------------
def random_testing_project_kwargs():
    kwargs = dict(company='ouroboros',
                  namespace='testing',
                  project=f'testing{random.randint(1, 100000)}',
                  pythonversion='3.6')
    env = f'{kwargs["company"]}-{kwargs["namespace"]}-{kwargs["project"]}'
    return dict(kwargs=kwargs, env=env)
