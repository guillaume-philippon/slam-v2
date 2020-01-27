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

MariaDB
#######

We will use MariaDB to store information. CentOS 7 hasn't got enough recent sqlite
version for Django but you could use sqlite or other Django 3 database backend for
SLAM.

.. code-block:: bash

    root@slam# systemctl enable mariadb
    root@slam# systemctl start mariadb
    root@slam# mysql -h localhost -u root
    MariaDB [(none)]> create database slam character set utf8;;
    MariaDB [(none)]> grant all privileges on slam.* to 'slamdb'@'localhost' identified by 'slamdbpass';
    MariaDB [(none)]> quit;
    MariaDB [(none)]> SET sql_mode='STRICT_TRANS_TABLES';
    MariaDB [(none)]> SET sql_mode='STRICT_ALL_TABLES';

Python Virtualenv
#################

.. code-block:: bash

    root@slam# python3 --version
    Python 3.6.8
    root@slam# mkdir -p /opt/slam
    root@slam# cd /opt/slam
    root@slam# git clone https://github.com/guillaume-philippon/slam-v2.git
    root@slam# python3 -m venv venv
    root@slam# source /opt/slam/venv/bin/active
    root@slam# pip install --upgrade pip
    root@slam# pip install -r requirements.txt
    root@slam# pip install mysqlclient

Django
######

Django configuration is done on /opt/slam/slam/settings.py file.

.. code-block:: python

    ALLOWED_HOSTS = [ 'slam-public-ip' ]
    ...
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {
                'read_default_file': os.path.join(BASE_DIR, 'my.cnf')
                }
            }
        }

You also need put database credential on /opt/slam/slam/my.cnf

.. code-block:: ini

    [client]
    database = slam
    user = slamdb
    password = slamdbpass
    default-character-set = utf8%

Git
###

SLAM create configuration file and put it into a git repository. You can look @ github or gitlab to
have a repository to store data. You will need to clone this git repository on SLAM server

.. code-block:: bash

    root@slam# cd /opt/slam/slam
    root@slam# mkdir build
    root@slam# cd build
    root@slam# git clone https://git.example.com/my-repo .
    root@slam# chown -R uwsgi:uwsgi .

