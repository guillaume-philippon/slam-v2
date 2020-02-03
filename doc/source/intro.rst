Introduction
============

SLAM (Super LAN Address Manager) is a IPAM developped by IJCLab IT department.
It is design to give a easy way for IT crew member to provide IP and Network
access for user. To do that, SLAM produce configuration for 3 differents services:

    * ISC-DHCP_: for each machine with MAC adress and fixed IP address, SLAM produce
      isc-dhcp configuration
    * ISC-Bind9_: SLAM can manage A, AAAA and CNAME records for a domain. It can also
      manage cross-domain CNAME and reverse DNS.
    * freeradius_: SLAM can produce a freeradius users file to provide MAC address
      authentication and VLAN configuration

Credits
-------
We use some set of framework and toolkit provided by community, included

For web interface:

* jQuery_
* Bootstrap_
* DataTables_

For backend:

* Django_
* git_

For documentation:

* Sphinx_

.. _ISC-DHCP: https://www.isc.org/dhcp/
.. _ISC-Bind9: https://www.isc.org/bind/
.. _freeradius: https://freeradius.org/
.. _jQuery: https://jquery.com/
.. _Bootstrap: https://getbootstrap.com/
.. _DataTables: https://datatables.net
.. _Django: https://www.djangoproject.com/
.. _Sphinx: http://www.sphinx-doc.org/
.. _git: https://git-scm.com/