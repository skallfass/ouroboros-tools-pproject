Concepts
********

.. contents::

Complete pproject workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^
The following figure illustrates how a typical workflow inside pproject usage
looks like and which stations in development-circle correspond to which
pproject-command.

.. figure:: _static/pproject_workflow_new.svg
    :align: center
    :width: 50 %

Using groups inside vcs
^^^^^^^^^^^^^^^^^^^^^^^

.. note::
    Groups currently can only be used when using **gitlab** as vcs inside
    config. pproject doesn't support github-teams yet.

    Valid group formats:
        * COMPANY-NAMESPACE
        * COMPANY-COMBINED_NAMESPACE

Using groups create the possibility to set different **visibility rules**
and **access authorizations** for each kind of project individually.

Developing inside conda-environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Projects often depend on a specific python-version and multiple third-party
packages like psycopg2, attrs, pandas, etc. The syntax and functionalities of
these packages may change or be deprecated in former or future versions.
Thats why it is always important to develop inside strict defined
environments. There are a lot of possibilities for that: using pip with
virtualenv, pipenv, docker, etc. One of these possibilities are
conda-environments which are used in pproject.

Using the meta.yaml as conda-environment definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The idea to use the **meta.yaml as the environment-definition** instead of using
the use environment.yml file was inspired by **David Wölfle**.

At this point:
    Thanks a lot to David for this awesome idea!

If you build a **conda-package**, the meta.yaml definition is used to collect
the **package dependencies**. Using an additional **environment.yml** is
error-prone and redundant information.
Creating an environment based on the information in the meta.yaml at the
**requirements-run-section** allows more **flexibility** for the
versions of the dependencies (you can set >, <, >=, <=, and x* version-numbers)
then in the environment.yml definition which uses
**exact version-definitions**.
You also make sure to develop in the same environment as resulting in the
environment in which you install the resulting package.
It also provide the development of a project with multiple developers, all
using the same environment like they would use the same environment.yml-file.

The **pproject update** and **pproject autoenv** commands collect the
dependency-informations as defined in the
**meta.yaml’s requirements-run-section** and creates an conda-environment based
on these dependencies.
If the environment already exists, it will be removed and recreated based on
the new definiton.
This pretends the environment to include dependency-zombies from former
environment-definitions.
So make sure to place all your dependencies inside the
requirements-run-section of the meta.yaml.

.. warning::
    All other installations (conda install) and deletions (conda remove)
    inside the conda environment will be reset after the next
    **pproject update** execution (either triggered by pproject autoenv or
    manually run).

If **pproject autoenv** recognizes a change inside the meta.yaml file
(based on md5sum-comparison saved in the hash.md5 file), **pproject update** is
triggered.
If you didn’t activate the autoupdate with **pproject autoupdate_toggle**
(in .bashrc/.zshrc or manually), you can run the **pproject update** command
yourself.


Using entry-points
^^^^^^^^^^^^^^^^^^
If you developed a products, operations or services package it is meaningful
to set an entry point for your main function inside the meta.yaml file.
This allows to run your project after build with a short command like

.. code-block:: bash

    /var/local/conda/envs/ouroboros-products-dummy/bin/dummy --help

You can also use:

.. code-block:: bash

    source activate ouroboros-products-dummy
    dummy --help

If you don’t use an entry-point you’ll have to use a possibly really long
command like the following to execute your project:

.. code-block:: bash

    /var/local/conda/envs/ouroboros-products-dummy/bin/python /var/local/conda/envs/ouroboros-products-dummy/lib/python3.6/site-packages/ouroboros-products-dummy/ouroboros/products/dummy/dummy.py --help

Thats why it is recommended to use entry-points. Especially if you want to use
readable cronjos for your project or if your resulting project is used often.

pproject project structure
^^^^^^^^^^^^^^^^^^^^^^^^^^
The used skeletons can be found at:

* https://github.com/skallfass/skeleton
* https://gitlab.com/skallfass-ouroboros/skeleton

.. code-block:: bash

    COMPANYNAME-NAMESPACE-PROJECT
    ├── build (after using sphinx)
    ├── conda-build
    │   ├── hash.md5
    │   └── meta.yaml
    ├── COMPANY
    │   ├── __init__.py
    │   └── NAMESPACE
    │       ├── PROJECT
    │       │   ├── __init__.py
    │       │   └── YOUR_CODE.py
    │       └── __init__.py
    ├── README.md
    ├── setup.py
    ├── source (after using sphinx)
    └── tests
        ├── __init__.py
        └── test_YOUR_CODE.py


Your project dependencies are stored in **conda-build/meta.yaml**.
Whenever you add a **new dependency** (import) to your code, add this dependency
to the **requirements-run-section** inside your meta.yaml. If **autoenv** is
set inside the precommand and **autoupdate_toggle** is **on**,
**pproject** detects the changes in your meta.yaml file and automatically
rebuilds your **conda-environment**. If autoenv is disabled you can run this
step manually from inside the folder **company-namespace-project** with

.. code-block:: bash

    pproject update

If **autoenv** is activated the corresponding conda-environment for your project
is activated in shell when entering the **company-namespace-project**-folder.
If you leave this folder, the environment is deactivated. Please note, that
any dependency added to your environment with "conda install" is removed from
the environment if **pproject update** is triggered
(either from autoenv or manually).
All dependencies have to be placed inside the meta.yaml.
Important: don't edit the hash.md5 file, the content of this file is managed
by pproject to decide if rebuild of the environment is necessary or not.

.. note::
    Please store all your tests in the **tests**-folder, so **pproject test**
    can find them.
    Don't edit the **setup.py** if not really needed and you're not really
    sure what you are doing (the content is automatically
    build from the **pproject create** command and is required for the
    conda-package build process).
