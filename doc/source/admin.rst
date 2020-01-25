Administrator Guide
===================

SLAM is splitted into 2 differents components. A command line interface project
called slam-v2-cli and a Django based web services.

This guide will only provide information about web servies. For more information
about the CLI, you must look at the project pages.

Installation
------------

SLAM has been based on python 3.6 and Django 3.0. It should work with
all Operating System supported by python 3.6 and Django 3.0 but we had done
the configuration on CentOS 7 machine and we will describe the installation
step for CentOS 7.

CentOS 7
########

We need to install EPEL to have access to python36 modules.

.. code-block:: bash

    root@slam# yum install -y epel-release
    root@slam# yum -y update
    root@slam# yum install -y git uwsgi-plugin-python36 mod_proxy_uwsgi mariadb-server mariadb-devel gcc python3-devel

Python Virtualenv
#################

