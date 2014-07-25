eheritage
=========
The aim of this project is to produce an Australian Heritage Portal, the main feature being a federated search across the Queensland and Victorian Heritage Registers. This is being developed with aim to expand to include all relevant heritage registers across Australia.


Development Installation
------------------------
Python project dependencies can be installed into a `virtualenv`, which can be activated and deactivated from the shell. The easiest way to work with virtual environments is to use `virtualenvwrapper`, which adds `mkvirtualenv`, `workon` and `deactivate` commands, among others.

Install virtualenvwrapper:

    sudo apt-get install virtualenvwrapper

Create a virtualenv for this project:

    mkvirtualenv eheritage

This will automatically activate the environment. In future, it can be activated using:

    workon eheritage

Clone a local copy of the project:

    git clone https://github.com/uq-eresearch/eheritage.git

Install dependencies of the project:

    pip install --requirement requirements.txt

Use development settings:

    cp devconfig.sample devconfig.cfg
    export EHERITAGE_SETTINGS=$HOME/eheritage/devconfig.cfg
    # Or whatever your local path to a development settings file is

And use development settings automatically when activating your virtualenv by adding the environment setting to a post-activate hook:

    cdvirtualenv
    echo "export EHERITAGE_SETTINGS=$HOME/eheritage/devconfig.cfg" >> bin/postactivate
    cdproject

Run the e-Heritage portal development server:

    ./run.py

The development server will reload automatically when anything is edited.


Production Deployment
---------------------

An ansible playbook is supplied to deploy the e-Heritage Portal and all required software to a fresh Ubuntu 14.04 instance.

The playbook depends on some external git repositories included as submodules, these must be downloaded first:

    git submodule update --init

Install ansible system-wide on Ubuntu:

    sudo apt-get install ansible

Or into a virtualenv:

    pip install ansible

Run the playbook against your remote server:

    ansible-playbook -v -i deployment/hosts deployment/server_setup.yml
