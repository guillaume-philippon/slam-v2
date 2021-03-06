RESTFul API
===========

The SLAM RESTful API allow user to manipulate all part of SLAM configuration. It use HTTP method
to describe the action and unique resource identifier (URI) to locate the objects. Objects are
composed by fields and sets of sub-objects. Per example, a networks is composed by fields like
a description, a dns-server and by a set of IP address.

When we want to modify a field, we update the object. When we want to add or remove a sub-object,
we create a delete a sub-object.


URI hierarchy
-------------

* **/**: all objects in databases (ex. https://slam.example.com/)
* **/networks/**: all networks in databases (ex. https://slam.example.com/networks/)
* **/networks/<network>**: a spectic network (ex. https://slam.example.com/networks/net-example/)
* **/networks/<network>/<IP-address>**: a specific IP address in a network
  (ex. https://slam.example.com/networks/net-example/192.168.0.1)
* **/domains/**: all domains in databases (ex. https://slam.example.com/domains/)
* **/domains/<domain>**: a specific domain (ex. https://slam.example.com/domains/example.com)
* **/domains/<domains>/<record>**: a specific record
  (ex. https://slam.example.com/domains/example.com/www)

HTTP method
-----------

* **GET**: to get information
* **POST**: to create a new object
* **PUT**: to update object information
* **DELETE**: to delete a object

Hosts API
---------

Through API, you can manipulation hosts. The base URI for hosts is https://slam.example.com/hosts

Creation
########
Creation is done by POST HTTP method with the following data:
* interface: the MAC address of the network interface
* owner: the owner of the machine
* network: the network we want to use
* ip_address: if we want to specify a IP address
* no_ip: if we don't want IP address. It will provide radius configuration but no IP address will be
  associated to the machine
* dhcp: if we want (or not) DHCP configuration
* ns: the name of the machine (fqdn will be ns+domain)
* domain: the domain name (fqdn will be ns+domain)
