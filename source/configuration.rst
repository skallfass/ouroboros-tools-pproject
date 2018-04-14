Configuration
*************

.. contents::

Set up git
^^^^^^^^^^
Install and set up git (set the username and email in the .gitconfig-file).

.. note::
    Configure git if not already done with your username and email:

    .. code-block:: bash

        git config --global user.name "John Doe"
        git config --global user.email johndoe@example.com


Grant acces to your remote vcs using tokens
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create an **access-token** for your remote-vcs (gitlab or github) and save it
inside a file (see "Create a gitlab-token"/"Create github-token" for details).

.. note::
    Create a gitlab-token:
        (See https://gitlab.com/profile/personal_access_tokens)

        1. Log in to your GitLab instance
        2. Go to **settings** > **Access Tokens**
        3. Add a personal access token, give it a name and scopes **api** and
           **read_registry**
        4. Click **create personal access token**
        5. Save this token to a file and set the filepath of the
           gitlab-token-file inside the pproject_config.yml
           (**~/.config/pproject/pproject_config.yml**) under **vcs**
           > **gitlab** > **token_path**.


.. note::
    Create a github-token:
        (See https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/)

        1. Log in to your GitHub instance
        2. Go to **settings** > **Developer settings** > **Personal access
           tokens**
        3. Add a personal access token, give it a name and scopes **repo**
        4. Click **Generate token**
        5. Save this token to a file and set the filepath of this file inside
           the pproject_config.yml (**~/.config/pproject/pproject_config.yml**)
           under **vcs** > **github** > **token_path**.

pproject_config.yml
^^^^^^^^^^^^^^^^^^^
Now edit the user pproject-config at
**~/.config/pproject/pproject_config.yml**:

.. code-block:: yaml

    # defines where conda is installed
    conda_folder: '/var/local/conda'


    # defines where the pproject-environment is installed
    pproject_env: '/var/local/conda/envs/pproject'


    # defines where to get the project-skeleton used for new project, from
    skeleton_repo: 'git@gitlab.com:skallfass/skeleton.git'


    # the company to use for new projects. Also used to combine the
    # gitlab-groups as "company-namespace".
    company: 'ouroboros'


    # Details about the remote-vcs you use.
    vcs:
        # available are:
        #     'gitlab'
        #     'github'
        use: 'github'

        gitlab:
            url: 'http://127.0.0.1:80'
            api: 'http://127.0.0.1:80/api/v4'
            # The path where your access-token is stored.
            # Required to interact with remote vcs out of pproject.
            token_path: '~/.config/pproject/.gitlab.token_test'
            ssh: 'ssh://git@localhost:50000'
            use_groups: true
            # namespaces available for project creation if no connection to vcs
            offline_namespaces:
                - 'testing'
                - 'products'
                - 'modules'
                - 'services'

        github:
            url: 'https://api.github.com'
            api: 'https://api.github.com/user/repos'
            # The path where your access-token is stored.
            # Required to interact with remote vcs out of pproject.
            token_path: '~/.config/pproject/.github.token'
            ssh: 'ssh://git@github.com'
            use_groups: false
            # namespaces available for project creation if no connection to vcs
            offline_namespaces:
                - 'testing'
                - 'products'
                - 'modules'
                - 'services'


    # To allow other users inside your network you should have set up an own
    # conda-repository-server. To allow pproject to publish conda-packages
    # built with pproject at this repository, the following settings are
    # required.
    conda_respository_server:
        # The connection to your conda-repository-server.
        user: 'user'
        host: 'hostname'
        # The path on your conda-repository-server where the conda-packages are
        # stored.
        packages_path: '/var/repopath'
        # The path to the conda-executable on the conda-repository-server.
        # Required to update the repository index with "conda index PATH" after
        # publishing of new packages.
        conda_exe: '/var/local/conda/bin/conda'


    # As default pytest inside pproject is configured to use the arguments as
    # defined here. If you don't change this parameters by placing it inside
    # your user-config, pytest uses the arguments "--cache-clear" and "-q" if
    # run from the pproject-tool. If you need more details like "-vv" or "-s",
    # place these arguments here.
    pytest_arguments:
        - "--cache-clear"
        - "-q"


Now make sure pproject is loaded inside terminal on each start by adding the
required content to your .zshrc/.bashrc.

.. note::
    To be able to publish built packages with pproject on your
    conda-repository-server (**pproject build --pulish**), you have to copy
    your public-ssh-key to the conda-repository-server.

.. note::
    To be able to release your built package as a conda-package in its own
    conda-environment with pproject on other hosts (**pproject release**) you
    have to add your public-ssh-key to the these hosts.


Bash
^^^^
Add the following content to your .bashrc.

.. code-block:: bash

    # Define where the pproject-environment is installed to
    export PPROJECT_FOLDER=/var/local/conda/envs/pproject

    if [ -f $PPROJECT_FOLDER/bin/pproject ]; then

        # Load the variable-definitions from the config file to be available
        # for the pproject.sh file
        declare $($PPROJECT_FOLDER/bin/pproject_read_config)

        # Load pproject inside bash so it can be used
        source $PPROJECT_FOLDER/bin/pproject

        # Activate autoactivation of conda-environments
        pproject autoenv_toggle

        # Activate autoupdate of conda-environments when changing
        # meta.yaml-content
        pproject autoupdate_toggle

        # Check and execute autoactivation and/or autoupdate (if these
        # functionalities are activated by the toggles) before each command
        # inside the commandline.
        PROMPT_COMMAND='pproject autoenv'
    fi

Zsh
^^^
Add the following content to your .zshrc.

.. code-block:: bash

    # Define where the pproject-environment is installed to
    export PPROJECT_FOLDER=/var/local/conda/envs/pproject

    if [ -f $PPROJECT_FOLDER/bin/pproject ]; then

        # Load the variable-definitions from the config file to be available
        # for the pproject.sh file
        declare $($PPROJECT_FOLDER/bin/pproject_read_config)

        # Load pproject inside bash so it can be used
        source $PPROJECT_FOLDER/bin/pproject

        # Activate autoactivation of conda-environments
        pproject autoenv_toggle

        # Activate autoupdate of conda-environments when changing
        # meta.yaml-content
        pproject autoupdate_toggle
    fi

    precmd() {
        # Check and execute autoactivation and/or autoupdate (if these
        # functionalities are activated by the toggles) before each command
        # inside the commandline.
        pproject autoenv;
    }

If you restart your terminal-session, you'll see the following output:

.. code-block:: bash

     ℹ              AUTOENV on
     ℹ           AUTOUPDATE on

Now pproject is ready to work with.
