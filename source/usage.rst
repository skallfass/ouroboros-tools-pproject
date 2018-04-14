Usage
*****

.. contents::


The pproject-tool is controlled with the command **pproject**.
Any pproject specific action is introduced with this command.
The following subcommands are available:

* info
* autoenv_toggle
* autoupdate_toggle
* autoenv
* create
* update
* test
* version
* build
* release
* sphinx


Example
^^^^^^^
Example how a project is created and **pproject autoenv_toggle** and
**pproject autoenv** is used inside a project:

    .. raw:: html

        <script src="https://asciinema.org/a/dvLi3cOmeE7XG9WHOvu8oRIRm.js" id="asciicast-dvLi3cOmeE7XG9WHOvu8oRIRm" async></script>


autoenv_toggle, autoupdate_toggle and autoenv
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

pproject autoenv_toggle
-----------------------
Toggles if autoactivation and deactivation is activated or not.

.. code-block:: bash

    pproject autoenv_toggle
    >> ℹ      AUTOACTIVATE off

    pproject autoenv_toggle
    >> ℹ      AUTOACTIVATE on


Automatically activates environment if conda-build/meta.yaml file exists and
deactivates the environment if folder is leaved.

pproject autoupdate_toggle
--------------------------
Toggles if autoupdate of project is activated or not.

Changes in the meta.yaml when inside the projects-root-folder trigger
**pproject update** automatically.

.. code-block:: bash

    pproject autoupdate_toggle
    >> ℹ      AUTOUPDATE off

    pproject autoupdate_toggle
    >> ℹ      AUTOUPDATE on


pproject autoenv
----------------
This command is only used inside the .bashrc/.zshrc. Normally the user doesn't
have to use this command. It triggers the **source activate/deactivate** and
**pproject update** commands to activate/deactivate the projects
conda-environment and updates the environment if changes in the meta.yaml
are recognized.

.. code-block:: bash

    pproject autoenv


pproject create
^^^^^^^^^^^^^^^
If you use gitlab as your vcs and have set the use-groups-flag inside the
config file, the available namespaces for your project creation are collected
from the gitlab-instance as defined in the config-file using your token.
These namespaces are your group-names minus your company-name.

For example:
    Your company-name is "example". Then all your groups have to
    start with "example-". Valid would be for example: "example-testing",
    "example-modules", etc.

If not connection to your gitlab is possible, the offline namespaces as
defined in the config-file are used.


The default setting for project creation is to create it local.
In this case the created project will be n initialized git repository, but the
remote-origin isn't set.
Only if the **--remote** flag is passed, it will also be created on your
remote vcs and the origin-url of the project is automatically set.
Then, after creation, all created files are added, commited and pushed to the
remote.

.. note::
    currently only the following pythonversions are supported:

    * 2.7
    * 3.6

.. code-block:: bash

    pproject create [--remote] {NAMESPACES} -n PROJECTNAME [-p PYTHONVERSION]


pproject update
^^^^^^^^^^^^^^^
Creates a **conda-environment** based on the information inside the
**conda-build/meta.yaml**-file. If the environment already exists it will be
removed and **recreated** to pretend dependency zombies.

.. code-block:: bash

    pproject update

.. note::
    This command isn't required to be run by the user if **autoupdate** is
    toggled inside your .bashrc/.zshrc cause the update is run each time you
    modify the projects meta.yaml-file.


pproject test
^^^^^^^^^^^^^
Uses `pytest <https://github.com/pytest-dev/pytest/>`_ to run all tests inside
the **tests**-folder.

.. code-block:: bash

    pproject test

.. note::
    The pytest settings during these tests can be customized inside the
    config-file at **~/.config/pproject/pproject_config.yml** inside
    **pytest_arguments**. Example:

    .. code-block:: yaml

        pytest_arguments:
            - '--cache-clear'
            - '-q'
            - '-s'

pproject version
^^^^^^^^^^^^^^^^
If you use pproject for your project you have to use **semantic versioning** style
for your projects versionnumber. This means your versionnumber is
a combination of **"majorversion.minorversion.patchversion"**.
For details about semantic versioning see https://semver.org/ for details.

.. code-block:: bash

    pproject version -m "MESSAGE" {major, minor, patch}

Example
-------
Assume the current version is "0.0.1"

The changes made in the project should result in a major-release.

After adding, commiting and pushing the changes to the origin run the
following pproject-command:

.. code-block:: bash

    pproject version -m "Changes in ..." major

This results in the new version-tag "1.0.0".
The tag is finally pushed to gitlab.


pproject build
^^^^^^^^^^^^^^
Creates a conda-package of your project with the current git tag (set with
**pproject version**).
First updates the environment using **pproject update** to use the latest
project-conda-environment.
Then **pproject test** is run to test if all tests of your project as defined
in the **tests**-folder succeed.
If there isn't any uncommited stuff in your project and it is tagged, the
conda-package is build and added to your local **conda-build-folder**.
If you passed the flag **--publish** it will also be published to your
conda-repository server as defined in your config-file.

Steps being run:
    * updating environment
    * testing your project else breaks
    * checking for uncommited stuff in your project else breaks
    * checking if git-tagged else breaks
    * checking if git-tag also pushed to origin else breaks
    * building conda-package
    * (copying your package to the conda-repository server [OPTIONAL])

.. code-block:: bash

    pproject build [--publish]

.. note::
    For publishing packages to your conda-repository-server after build you
    have to customize your user-config-file at
    **~/.config/pproject/pproject_config.yml**.
    Set the following variables with your own values:

    .. code-block:: yaml

        # ssh-connection-options to the conda-repository-server
        conda_repo_userathost: 'user@host'

        # path on the conda-repository-server where your conda-bld/linux-64
        # folder is located
        conda_repo_pkgs_path: '/var/repopath'

        # path to your conda-executable
        conda_repo_conda_bin: '/var/local/conda/bin/conda'

pproject info
^^^^^^^^^^^^^
The pproject info command is seperated into two commands:

* pproject info general
* pproject info project

pproject info general
---------------------
This command is used to show current settings of the pproject-tool.

.. code-block:: bash

    pproject info general

Example output:
    .. code-block:: bash

        ========================================================== GENERAL PPROJECT-INFO
        ..................version  0.0.13
        ..................autoenv  on
        ...............autoupdate  on

        ========================================================================= CONFIG
        .............conda_folder  /var/local/conda
        ...........meta_yaml_path  conda-build/meta.yaml
        .......meta_yaml_md5_path  conda-build/hash.md5
        .............pproject_env  /var/local/conda/envs/pproject
        ............skeleton_repo  git@gitlab.com:skallfass-ouroboros/skeleton.git
        ..................company  ouroboros
        ......................vcs
        ...........................use  gitlab
        ........................gitlab
        ..........................................url  http://127.0.0.1:80
        ..........................................api  http://127.0.0.1:80/api/v4
        ...................................token_path  ~/.config/pproject/.gitlab.token_test
        ..........................................ssh  ssh://git@localhost:50000
        ...................................use_groups  True
        ...........................offline_namespaces  ['testing', 'products', 'modules', 'services']
        ........................github
        ..........................................url  https://api.github.com
        ..........................................api  https://api.github.com/user/repos
        ...................................token_path  ~/.config/pproject/.github.token
        ..........................................ssh  ssh://git@github.com
        ...................................use_groups  False
        ...........................offline_namespaces  ['testing', 'products', 'modules', 'services']
        .conda_respository_server
        ..........................user  user
        ..........................host  hostname
        .................packages_path  /var/repopath
        .....................conda_exe  /var/local/conda/bin/conda
        .........pytest_arguments  ['--cache-clear', '-q']

        ===================================================================== NAMESPACES
        ....................GROUP  ID
        ..................testing  2

pproject info project
---------------------
This command is used to show details of the current project.

.. warning::
    This command can only be used inside pproject-created projects!

.. code-block:: bash

    pproject info general

Example output:

    .. code-block:: bash

        =================================================================== PROJECT INFO
        ..................... name  ouroboros-testing-example
        ................. reponame  ouroboros-testing-example
        ...... current version-tag  0.0.0
        ............ pythonversion  3.6
        ............. dependencies - python 3.6*
        .......................... - pytest
        .......................... - ipython
        .......................... - pylint


pproject release
^^^^^^^^^^^^^^^^
Releases your project as a conda-package in its own environment
(environmentname: **CONDAPACKAGENAME_env**, if your don't pass another
environment-name using the **-e**-parameter) on the destination host (name
passed with the **-d** parameter).

.. warning::
    This command can only succeed if your public ssh-key is already stored at
    the destination host. If that is not the case, yet, you can paste your
    publish ssh-key on the destination server like the following:

    .. code-block:: bash

        ssh-copy-id USERNAME@HOSTNAME

    If you don't have a ssh-key yet, you have to generate one before the
    previous command like the following (make sure **openssh** is already
    installed):

    .. code-block:: bash

        ssh-keygen -t rsa -b 4096 -C "YOUR_EMAIL"

Steps being run:
    * updating environment.
    * testing your project else breaks.
    * checking for uncommited stuff in your project else breaks.
    * checking if git-tagged else breaks.
    * checking if git-tag also pushed to origin else breaks.
    * building conda-package.
    * copying your package to the conda-repository server.
    * creating environment on destination host with created package installed
      inside (if already exists it is removed and replaced).
    * add changes to destination-hosts **~/.pproject.log** file for
      traceability.

.. code-block:: bash

    pproject release -d USERNAME@HOSTNAME [-e ENVIRONMENT_NAME]

.. note::
    For traceability reason releasing a package with **pproject release**
    stores information about when which user released what on the server.

    These informations are stored inside **~/.pproject.log** on the
    destination server.

    The result looks like the following:

        .. code-block:: bash

            2018-03-24T12:49:59.432033 [ektom@gallifrey] CREATE ouroboros-testing-example_env [SOURCE: master 1.0.1]


pproject sphinx
^^^^^^^^^^^^^^^
This command creates both a html- and a pdf-sphinx documentation of your
project using the read-the-docs-theme. Please make sure to use the numpy- or
google-documentation-style inside your code.

.. code-block:: bash

    pproject sphinx

Resulting in two new folders:

* build
* source

Inside the source folder, the files on which the resulting documentations are
based are stored. You can customize the inlcuding **rst-files** as you need.
Running **pproject sphinx** again creates the resulting pdf- and html-files
inside the build-folder.
