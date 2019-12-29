# slam-v2

## Quick intallation guide
This guide was written based on CentOS 7. As soon as you can have python 3 your OS can support
SLAM-v2.

OS base installation

    # yum install -y epel-release
    # yum -y update
    # yum install -y git uwsgi-plugin-python36 mod_proxy_uwsgi mariadb-server mariadb-devel gcc python3-devel

MariaDB configuration

    # systemctl enable mariadb
    # systemctl start mariadb
    # mysql -h localhost -u root
    MariaDB [(none)]> create database slam character set utf8;;
    MariaDB [(none)]> grant all privileges on slam.* to 'slamdb'@'localhost' identified by 'slamdbpass';
    MariaDB [(none)]> quit;
    MariaDB [(none)]> SET sql_mode='STRICT_TRANS_TABLES';
    MariaDB [(none)]> SET sql_mode='STRICT_ALL_TABLES';

Python configuration

    # python --version
    Python 3.6.8
    # mkdir -p /opt/slam
    # cd /opt/slam
    # git clone https://github.com/guillaume-philippon/slam-v2.git
    # cd slam-v2
    # python -m venv /opt/slam/venv
    # source /opt/slam/venv/bin/active
    # pip install --upgrade pip
    # pip install -r requirements.txt
    # pip install mysqlclient

django configuration for slam you need to change in slam/slam/settings.py database block by

    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'my.cnf')
            }
        }
    }

and run the following commands

    # python slam/manage.py makemigrations
    # python slam/manage.py migrate
    # python slam/manage.py createsuperuser # to create a administrator
    
    