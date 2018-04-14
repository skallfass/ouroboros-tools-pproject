Installation
************

.. contents::

System requirements
^^^^^^^^^^^^^^^^^^^

.. warning::
    pproject is designed for linux systems. OS X should also work, but Windows
    is not supported yet.

You need `conda <https://conda.io/docs/>`_
(`Anaconda <https://conda.io/docs/glossary.html#anaconda-glossary>`_ /
`Miniconda <https://conda.io/docs/glossary.html#miniconda-glossary>`_) with
`conda-build <https://github.com/conda/conda-build>`_ installed for this tool.

git has to be installed and configured (user.name and user.email set in the
.gitconfig), too.

.. warning::
    Currently pproject only supports the following vcs:
        * github
        * gitlab (on gitlab.com or self-hosted)

.. note::
    For installation instructions of conda see:
        https://conda.io/docs/user-guide/install/index.html.

.. note::
    For conda-build see:
        https://conda.io/docs/user-guide/tasks/build-packages/install-conda-build.html.

.. note::
    Alternatively use the following to install miniconda including conda-build
    and set folder permissions and conda-installation-path as required by the
    pproject-tool:

        .. code:: bash

            export CONDADIR=/var/local/conda
            mkdir -p $CONDADIR
            curl -L https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh
            /bin/bash /tmp/miniconda.sh -f -b -p $CONDADIR
            rm /tmp/miniconda.sh
            $CONDADIR/bin/conda install conda-build
            rm -r $CONDADIR/pkgs/*
            sudo groupadd condausers
            sudo usermod -aG condausers $USER
            sudo chown -R :condausers $CONDADIR
            sudo chmod -R 775 $CONDADIR


For creation of pdf-documentations for your projects you'll also need the
following packages:

* texlive-base
* latexmk
* texlive-fonts-recommended
* texlive-latex-recommended
* texlive-latex-extra

pproject supports the following shells:

* bash
* zsh


Installation
^^^^^^^^^^^^

.. code-block:: bash

    conda create -n pproject python=3.6 ouroboros-tools-pproject -c https://www.repository-channel.ouroboros.info/

