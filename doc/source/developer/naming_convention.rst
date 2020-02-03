Naming convention
=================

For SLAM development, we use a internal nomenclature to help new developer to come into
the code.

Object naming:

* **domain**: a domain is a DNS domain or sub-domain (ie example.com, department.example.com, ...).
* **entry**: a entry is a DNS record. This shoud be renamed to record.
* **network**: a network is a internet protocol (IPv4 or IPv6) network (ie 192.168.0.0/24, 2001::0/48,
  ...).
* **address**: a address is a unique IP address (both v4 or v6) (ie 192.168.0.24).
* **hardware**: a hardware is a description of physical machine.
* **interface**: a interface is a network interface, mainly describe by its mac address. A physical
  machine can have more than one interface.
* **inventory**: a inventory is a set of hardware.

Generic naming:

* **plurials**: we use plurials to describe a set of object. We don't care if it's a dict or a list.
* **<variable>_<xxx>**: in case we need to construct some specific part before add it in result, we
  use <variable>_<xxx> variable where xxx is the name of the object (per example: result_interfaces)
* **plugin**: a plugin define the kind of output (radius, dhcp, named, ...)
* **option**: a option is parameter that we will be used as a parameter for a function. We usually
  use in plurial to construct a dict.
* **arg**: equivalent to option
* **result**: a result is the value that will be return at the end of the function or method.
* **data**: data sent by user through RESTful API or web interface.
* **raw**: in some cases, we need to get a unstructured version of data. In this case, we called
  it raw before restructured the data.
* **rest_api**: is set to true if user used RESTful API.
* **uri**: the unique resource identifier of the object (used by web / RESTful API).

Methods and functions:

* **view**: a view is Django view, this is the interface between user (CLI or web interface) and
  database
* **show**: show is used to get a json version of the objects