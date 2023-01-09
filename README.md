# SLAM Quick intallation guide

This installation guide applies to SLAM v2. It was written based on CentOS 8 but should work 
on CentOS too. The most critial requirement is Python 3 which is available on both platforms 
through Python distribution like [PyEnv](https://github.com/pyenv/pyenv) or
[Anaconda](https://www.anaconda.com/products/distribution).

## OS installation

    # yum install -y epel-release
    # yum -y update
    # yum install -y git mariadb-server mariadb-devel

## MariaDB configuration

    # systemctl enable mariadb
    # systemctl start mariadb
    # mysql -h localhost -u root
    MariaDB [(none)]> create database slam character set utf8;;
    MariaDB [(none)]> grant all privileges on slam.* to 'slamdb'@'localhost' identified by 'slamdbpass';
    MariaDB [(none)]> quit;
 

## Python installation and configuration

It is recommended to install a Python distribution independent of the OS distribution as Python
provided by the OS is driven by OS needs and tends to be a source of problems with dependencies
used in application like SLAM. It is also recommended to use a distribution allowing to define
a "virtual environment" for the application, to isolate from Python configuration changes driven
by other applications. The current guide describe such an installation using 
[PyEnv](https://github.com/pyenv/pyenv). The current guide assumes PyEnv will be installed in
`/opt/pyenv` and that SLAM will be installed under `/opt/slam` but you can use the location you want.

* Python installation from PyEnv
  * Ensure you have the required OS packages installed for the Python installation as it will be
  rebuilt from sources:
  
  ```bash
  yum install -y libjpeg-turbo-devel libxslt-devel libxml2-devel libffi-devel pcre-devel libyaml-devel zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel findutils libuuid-devel tar
  ```
  * Download PyEnv installer:

  ```bash
  wget -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer
  ```
  
  * Define `PYVENV_ROOT` environment variable to the location where you want PyEnv to be installed.
  The specified directory must not exist.

  * Run the installer script. Once it has completed, it gives the instruction to activate PyEnv.

  ```bash
  ./pyenv-installer
  # Execute the mentioned commands (typically added in your ~/.bashrc) to activate PyEnv
  ```

    * Check the Python version available and install the last v3 production version (>= 3.9))

  ```bash
  pyenv install --list |egrep '^\s*3'
  pyenv install selected_version
  pyenv global selected_version
  ```
  
  * Check that the installed version is in your path

  ```bash
  python --version
  ```
  
  * Create a Python virtualenv for SLAM and activate it

  ```bash
  mkdir -p /opt/slam
  python -m venv --upgrade-deps --prompt slam /opt/slam/.venv
  source /opt/slam/.venv/bin/activate
  ```

  * Check your current Python is located in the virtualenv (`/opt/slam/.venv`)

  ```bash
  which python
  ```
  
  * Install the Python packages required by SLAM

  ```bash
  pip install django django-auth-ldap GitPython paramiko mysqlclient six uwsgi
  ```

## SLAM installation

SLAM must be installed from sources.

  ```bash
  cd /opt/slam
  git clone https://github.com/guillaume-philippon/slam-v2.git
  ```


## SLAM configurartion 

SLAM configuration must be customized to reflect your site configuration by editing the file 
`slam/settings.py` in `/opt/slam/slam_v2`.  You need to review all settings containing paths
or URLs to adapt them to your site. In particular the default `DATABASE` variable must be replaced
by something similar to :

    ```
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'my.cnf')
            }
        }
    }
   ```

Once `setting.py` has been properly configured, run the following commands:

   ```bash
   cd /opt/slam/slam_v2
   python ./manage.py makemigrations
   python ./manage.py migrate
   python ./manage.py createsuperuser    # to create a administrator
   ```
    
    