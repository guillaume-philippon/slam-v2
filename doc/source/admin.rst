Administrator Guide
===================

SLAM is split into 2 different components. A command line interface project
called slam-v2-cli and a Django based web services called slam-v2.

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
    MariaDB [(none)]> create database slam character set utf8;
    MariaDB [(none)]> grant all privileges on slam.* to 'slamdb'@'localhost' identified by 'slamdbpass';
    MariaDB [(none)]> SET sql_mode='STRICT_TRANS_TABLES';
    MariaDB [(none)]> SET sql_mode='STRICT_ALL_TABLES';
    MariaDB [(none)]> quit;

Python Virtualenv
#################

.. code-block:: bash

    root@slam# python3 --version
    Python 3.6.8
    root@slam# mkdir -p /opt/slam
    root@slam# cd /opt/slam
    root@slam# git clone https://github.com/guillaume-philippon/slam-v2.git
    root@slam# python3 -m venv venv
    root@slam# source /opt/slam/venv/bin/activate
    root@slam# pip install --upgrade pip
    root@slam# pip install -r slam-v2/requirements.txt
    root@slam# pip install mysqlclient

Django
######

Django configuration is done on /opt/slam/slam-v2/slam/slam/settings.py file.

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

You also need put database credential on /opt/slam/slam-v2/slam/my.cnf

.. code-block:: ini

    [client]
    database = slam
    user = slamdb
    password = slamdbpass
    default-character-set = utf8

Git & ssh
#########

SLAM create configuration file and put it into a git repository. You can look @ github or gitlab to
have a repository to store data. You will need to clone this git repository on SLAM server

.. code-block:: bash

    root@slam# cd /opt/slam/slam-v2
    root@slam# mkdir build
    root@slam# cd build
    root@slam# git clone https://git.example.com/my-repo .
    root@slam# chown -R uwsgi:uwsgi .

Now, you need to create a ssh-key pair for uwsgi and put it on /opt/slam/slam-v2/ssh directory.
We also put a config file to avoid strict hostkey checking.

.. code-block:: bash

    root@slam# mkdir -p /opt/slam/slam-v2/ssh
    root@slam# ssh-keygen -t rsa -f /opt/slam/slam-v2/ssh/id_rsa
    root@slam# cat >> /etc/ssh_config << EOF
      StrictHostKeyChecking no
    EOF
    root@slam# # If you use selinux
    root@slam# chcon -t chcon -R -t httpd_sys_content_t /opt/slam/slam-v2/ssh

You will now need to allow access to git repository for /opt/slam/slam/ssh/id_rsa.pub key.

uwsgi && nginx
##############

Last part of the installation is configuring the uwsgi and nginx server.

.. code-block:: bash

    # On CentOS 7 some directory are not created by default through rpm
    root@slam# mkdir -p /run/uwsgi
    root@slam# chown uwsgi:uwsgi /run/uwsgi
    root@slam# mkdir -p /var/log/uwsgi/
    root@slam# chown -R uwsgi:uwsgi /var/log/uwsgi

    root@slam# cat > /etc/uwsgi.d/slam.ini
    [uwsgi]
    plugin = python36
    single-interpreter = true

    master=True
    pidfile=/tmp/project-master.pid
    vacuum=True
    max-requests=5000
    daemonize=/var/log/uwsgi/slam.log

    # chdir is required by Django to be the root of the project files
    chdir=/opt/slam/slam-v2
    touch-reload = /opt/slam/slam-v2/slam/slam/wsgi.py
    wsgi-file = /opt/slam/slam-v2/slam/slam/wsgi.py
    virtualenv = /opt/slam/venv

    socket = 127.0.0.1:8008
    stats = /var/run/uwsgi/slam.sock
    protocol = uwsgi
    EOF
    root@slam# chown -R uwsgi:uwsgi /etc/uwsgi.d/slam.ini
    root@slam# systemctl restart uwsgi

    # apache configuration
    root@slam# cd /etc/httpd/httpd.d
    root@slam# cat > slam.conf <<EOF
    LoadModule proxy_uwsgi_module modules/mod_proxy_uwsgi.so

    ErrorLog	logs/slam.errorlog
    CustomLog	logs/slam.accesslog common
    LogLevel	Warn

    Alias "/static" "/opt/slam/static"

    ProxyPass /static !
    ProxyPass / uwsgi://127.0.0.1:8008/

    <Directory /opt/slam/static>
        AllowOverride None
        Require all granted
    </Directory>
    EOF
    root@slam# systemctl restart httpd

Initialization
--------------

SLAM database
#############

To initialize SLAM, you need to install slam-v2-cli to create your first network and first domain.

.. code-block:: bash

    user@anywhere$ slam networks create --address 192.168.0.0 --prefix 24 net-example
    user@anywhere$ slam domains create example.com --dns-master 192.168.0.1

After creating your first network and domain, we will produce generic file.

.. code-block:: bash

    user@anywhere$ slam producer commit

You can check file created on /opt/slam/slam/build/bind. As there are no data, you will
only have a generic SOA file for bind. You need to edit it to put your specific configuration.

.. code-block:: bash

    root@slam# cd /opt/slam/slam/build/bind
    root@slam# cat example.com.soa.db
    $TTL    2H
    @ IN  SOA dns-master.example.com. contact.example.com. (
              2020011118 ; Serial
              7200          ; Refresh - 2hours
              1200          ; Retry - 20 minutess
              3600000       ; Expire - 6 weeks
              86400 )       ;  Minimum - 24 hours
    root@slam# cat >> example.com.db << EOF
    ; Include some local configuration
    $INCLUDE /var/named/example.com.local.db
    ; Include slam configuration
    $INCLUDE /var/named/slam/bind/example.com.db
    EOF

Services servers
################

Now, let's go to your DNS server (close to the same for DHCP or freeradius)

.. code-block:: bash

    # We first create a ssh-key, we will grant access to git repository
    root@dns# ssh-keygen -t rsa
    # We will clone the git repo
    root@dns# mkdir -p /var/named/slam
    root@dns# cd /var/named/slam
    root@dns# git clone https://git.example.com/my-repo .

We will also need to create a small bash script that will be call by SLAM when it want
to modify DNS record

.. code-block:: bash

    root@dns# cat > /usr/local/bin/slam-agent << EOF
    #!/bin/bash
    SLAM_DIR=/var/named/slam
    SLAM_SERVICES=named

    cd $SLAM_DIR
    git pull
    systemctl restart $SLAM_SERVICES
    EOF
    root@dns# chmod +x /usr/local/bin/slam-agent

And finaly all access to slam server in dns server

.. code-block:: bash

    root@slam# ssh-copy-id root@dns

First publish
#############

Now, on your slam client machine, you can ask for publishing

.. code-block:: bash

    user@anywhere$ slam producer publish

This action will:

* trig a git commit and git push action
* attempt a ssh connection to every dns, dhcp or freeradius declared and launch
  /usr/local/bin/slam-agent script
