Overview
========

SLAM is developed to provide abilities to IT crew member to give IP address for user. SLAM web
service provide two different services:

* a RESTful API: You can develop your own client to integrate SLAM into other tools
* a web interface: Develop to provide very basic action. The goal is to make usage easiest as
  possible

Storage backend
---------------

All data are store into a database managed by Django. Every database manager supported by
Django can be used to store data.

File configuration workflow
---------------------------

To provide configuration file, SLAM use git as a central shared filesystem. You can use every
git server which support sshkey based authentication.

SLAM will always dump all the contents of database on configuration file. There are no insert
or add method which means all manual file modification will be lost on the next SLAM run.

Configuration file is locally store into a directory named *build*. This directory is split
into one directory per supported system (isc-dhcp, bind, freeradius, ...) where all configuration
file will be put.

.. code-block:: bash

    root@slam# cd /opt/slam/slam/build
    root@slam# ls -l
    drwxr-xr-x. 2 uwsgi uwsgi 4096 Jan 27 17:10 bind
    drwxr-xr-x. 2 uwsgi uwsgi   19 Jan  8 14:41 freeradius
    drwxr-xr-x. 2 uwsgi uwsgi 4096 Jan 26 20:48 isc-dhcp
    -rw-r--r--. 1 uwsgi uwsgi   15 Jan  8 14:41 README.md
    root@slam#

As you can see, the directory is owned by uwsgi user. For basic installation (see Administrator
Guide) SLAM run as uwsgi user. This user **must** have a ssh-key authorized on git server to
push data in it and on service server (DNS, DHCP, freeradius) to trig the pull.

Commit & Push
#############

To produce and push configuration in production, SLAM use a specific workflow named commit & push.

* commit: will produce file in SLAM server, you can see the result of git diff action to see
  what will be changed in service.
* push: will push data on git server, connect on every service machine and call a scripted called
  slam-agent. slam-agent can be a home-made script but a basic one can be see as generic bash script
  as followed

.. code-block:: bash

    #!/bin/bash
    cd /var/slam/git-workspace
    git pull
    systemctl restart named freeradius dhcpd

Production
----------

ISC-DHCP
########

SLAM provide two set of file for every network that can be used by isc-dhcp. SLAM doesn't
provide the main dhcpd.conf file but you can use *include* directive to use (or not use)
SLAM dhcp file.

This is also a good way to keep a totally manual file for every configuration that can't be
provide by SLAM.

.. code-block::

    authoritative;
    [...]
    include "/var/slam/git-workspace/isc-dhcp/network-1.conf";
    [...]


ISC-BIND
########

SLAM provide two set of file for every domain. The first one will contents the SOA. It will
mainly be used to update the domain serial number (see bind configuration for more information).
The second one will provide bind9 records.

We will use $INCLUDE bind9 directive to include record file in SOA file. SOA file should be
initialize and put into git repository (see Administrator Guide).

.. code-block::

    $TTL	2H
    ;
    @	IN	SOA	ns1.example.com. dns-master.example.com. (
                2020011037	; Serial
                300		; Refresh - 0 hours
                1200		; Retry - 20 minutes
                3600000		; Expire - 6 weeks
                86400 )		; Minimum - 24 hours
    ;
        IN	NS	ns1.example.com.

        IN	A       192.168.0.1

    ; some external records
    $INCLUDE /var/named/manual.example.com.db

    ; slam generated record
    $INCLUDE /var/slam/git-workspace/bind/example.com.db

Freeradius
##########

SLAM provide a user file for freeradius that can be include into freeradius configuration.
