"""
This module provide a Host model and all associated method.
  - Host.show: method to return a dict abstraction of a Host
  - Host.create: a staticmethod to create a Host w/ some check associated to it
  - Host.update: a staticmethod to update Host field
  - Host.remove: a staticmethod to delete a Host w/ some check associated to it
  - Host.add: a staticmethod to add a IP to a Host
  - Host.get: a staticmethod to get a dict abstraction of a Host w/o instanciate it before
  - Host.search: a staticmethod to get all Host match the filter
"""
# As we use django models.Model, pylint fail to find objects method. We must disable pylint
# test E1101 (no-member)
# pylint: disable=E1101
from distutils.util import strtobool

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError

from slam_core.utils import error_message, name_validator
from slam_hardware.models import Interface
from slam_network.models import Network, Address
from slam_network.exceptions import NetworkFull
from slam_domain.models import DomainEntry, Domain


class Host(models.Model):
    """
    Host represent a association between hardware, network and domain name service
      - name: a name for the hosts, by default, the name fqdn of the host
      - addresses: a list of IP address. Should be one-to-many relation but for some mistake, it s a
        many-to-many relation...
      - interface: the MAC address of the host
      - network: the main network for the host (ie. where it will be put by freeradius)
      - creation_date: When Host has been created
      - dhcp: a flag to enable, disable DHCP configuration.
    """
    name = models.CharField(max_length=150, unique=True, validators=[name_validator])
    addresses = models.ManyToManyField(Address)
    interface = models.ForeignKey(Interface, on_delete=models.PROTECT, null=True, blank=True,
                                  unique=True)
    network = models.ForeignKey(Network, on_delete=models.PROTECT, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    dhcp = models.BooleanField(default=True)

    def show(self, short=False, key=False):
        """
        This method return a dict construction of the object. We have 3 types of output,
          - standard: all information about object it-self, short information about associated
            objects (like ForeignKey and ManyToManyField)
          - short: some basic information about object it-self, primary key of associated objects
          - key: primary key of the object

        :param short: if set to True, method return a short output
        :param key: if set to True, method return a key output. It will overwrite short param
        :return:
        """
        if key:
            result = {
                'name': self.name
            }
        elif short:
            result_address = []
            for address in self.addresses.all():
                result_address.append(address.show(key=True))
            if self.interface is None:
                result_interface = dict()
            else:
                result_interface = self.interface.show(key=True)
            if self.network is None:
                result_network = dict()
            else:
                result_network = self.network.show(key=True)
            result = {
                'name': self.name,
                'interface': result_interface,
                'addresses': result_address,
                'network': result_network,
            }
        else:
            result_address = []
            for address in self.addresses.all():
                result_address.append(address.show(short=True))
            if self.interface is None:
                result_interface = dict()
            else:
                result_interface = self.interface.show(short=True)
            if self.network is None:
                result_network = dict()
            else:
                result_network = self.network.show(key=True)
            result = {
                'name': self.name,
                'interface': result_interface,
                'addresses': result_address,
                'network': result_network,
                'creation_date': self.creation_date,
                'dhcp': self.dhcp
            }
        return result

    @staticmethod
    def create(name, address=None, interface=None, network=None, owner=None, dns_entry=None,
               options=None):
        """
        This is a custom method to create a host w/ some check like.
          - Interface: check if it exist and it s free. If not, create a new one.
          - Address: check if it exist,it s free and in the network. If no address as been provide,
            get a free IP from the network
          - NS record: A and PTR record will be created

        :param name: name of the Host
        :param address: IP address for the Host
        :param interface: interface associated to this Host
        :param network: network associated to this Host
        :param owner: the owner of this Host
        :param dns_entry: NS record for the Host
        :param options: Some other options like 'no_ip' to force not get IP (Host w/o IP)
        :return:
        """
        interface_host = None
        network_host = None
        address_host = None
        owner_host = None
        if options is None:
            options = {
                'no_ip': False,
                'dhcp': True
            }
        if owner is not None:
            owner_host = owner
        if network is None and\
                address is None:  # We need at least one of this options
            return error_message('host', name,
                                 'Integrity error Address or Network should be provide')
        if interface is not None and\
                interface != '':  # If we create a host with a interface
            try:  # We check if interface exist (we can only one @MAC
                interface_host = Interface.objects.get(mac_address=interface)
                try:  # We check if interface is already attached to a host
                    interface_host.host_set.get()
                    # if interface exist and is attached to a host, so we can't add a new host
                    return error_message('host', name, 'Integrity error Interface still exist !')
                except ObjectDoesNotExist:  # If not, so we are good, the interface is free
                    pass
            except ObjectDoesNotExist:  # If interface not exist, we create a new one
                # We generate a default HW name
                hardware_name = '{}-{}'.format(name.split('.', 1)[0], interface.replace(':', '-'))
                hardware_args = {
                    'owner': owner
                }
                # We create a interface and a hardware for this interface
                result = Interface.create(mac_address=interface, hardware=hardware_name,
                                          args=hardware_args)
                if result['status'] != 'done':  # If we failed to create the interface
                    return result
                # We get the new interface
                interface_host = Interface.objects.get(mac_address=interface)
        if network is not None:  # If we just provided network name information
            try:  # We get the network based on network name
                network_host = Network.objects.get(name=network)
            except ObjectDoesNotExist as err:  # If network doesn't exist, we return a error
                return error_message('host', name, err)
        if address is None and\
                network is not None and\
                not options['no_ip']:  # If we didn't provide address and ask for it
            try:  # We try to get a new IP from network
                address = str(network_host.get_free_ip())
            except NetworkFull:  # If network is full, we return a error
                return error_message('host', name, 'Network have not usued IP address')
        if address is not None:  # If we provide a specific IP address
            try:  # We get the address
                address_host = Address.objects.get(ip=address)
                if len(address_host.host_set.all()) != 0:  # If address is used by another host
                    return error_message('host', name, 'Address is used by another host')
            except ObjectDoesNotExist:  # If address not exist, we create it
                # We check if address is in the right network
                network_host = Address.match_network(address)
                if network_host is None:
                    return error_message('host', name, 'No network found for {}'.format(address))
                if dns_entry is not None:  # If we provide a NS record we create the address w/ it.
                    result = Address.create(ip=address, network=network_host.name,
                                            ns_entry=dns_entry)
                    if result['status'] != 'done':  # If something go wrong
                        return result
                else:  # If we didn't provide a NS record, we just create the address w/o NS record.
                    result = Address.create(ip=address, network=network_host.name)
                    if result['status'] != 'done':
                        return result
                # We get address created
                address_host = Address.objects.get(ip=address)
        args = {
            'name': name,
            'interface': interface_host,
            'network': network_host,
        }
        if options['dhcp'] is not None:  # If we provided a specific value for DHCP generation
            args['dhcp'] = options['dhcp']
        try:
            host = Host(**args)
            host.full_clean()
            host.save()
            if address_host is not None:
                host.addresses.add(address_host)
            # We will return a dict representation and a status
            result = host.show()
            result['status'] = 'done'
            return result
        except (ObjectDoesNotExist, IntegrityError, ValidationError) as err:
            return error_message('host', name, err)

    @staticmethod
    def update(name, address=None, interface=None, network=None, dns_entry=None, dhcp=None):
        """
        This is a custom method to update a Host. Depending of options give, the rightfull field.

        :param name: name of the host (not used to update but to retrieve Host)
        :param address: IP address of the host
        :param interface: mac-address of the host
        :param network: network of the host
        :param dns_entry: NS record of the host
        :param dhcp: should DHCP be generated
        :return:
        """
        try:
            host = Host.objects.get(name=name)
            if interface is not None:
                if interface == '':  # If interface name is '' then, we want to remove interface
                    host.interface = None
                else:  # else, we update it.
                    try:
                        host.interface = Interface.objects.get(mac_address=interface)
                    except ObjectDoesNotExist:
                        result_interface = Interface.create(mac_address=interface,
                                                            hardware='{}-{}'.
                                                            format(name.split('.', 1)[0],
                                                                   interface.replace(':', '-')))
                        if result_interface['status'] == 'done':
                            host.interface = Interface.objects.get(mac_address=interface)
                        else:
                            return error_message('host', name, result_interface['message'])
            if network is not None:  # If we want to update the network, we need to get it.
                host.network = Network.objects.get(name=network)
            if dns_entry is not None:  # If we want to update the NS record, we need to get.
                domain_entry = Domain.objects.get(name=dns_entry['domain'])
                host.dns_entry = DomainEntry.objects.get(name=dns_entry['ns'], domain=domain_entry)
            if dhcp is not None:  # If we want to update DHCP flag
                host.dhcp = strtobool(dhcp)
            try:  # We check the validity of the object
                host.full_clean()
            except ValidationError as err:
                return error_message('host', name, err)
            host.save()  # We save it
        except ObjectDoesNotExist as err:  # If any object we try to get not exist, we return a
            # error.
            return error_message('host', name, err)
        return {
            'host': name,
            'status': 'done'
        }

    @staticmethod
    def remove(name, addresses=True, hardware=False, dns_entry=True):
        """
        This method is a method to delete a Host. As django use a internal method called delete
        to delete a instanciated object, we call the method remove.

        :param name: name of host
        :param addresses: if set to True, we also delete all addresses (default: True)
        :param hardware: if set to True, we also delete hardware (default: False)
        :param dns_entry: if set to True, we also delete dns_entry (default: True)
        :return:
        """
        hardware_host = None
        try:  # We need to get the object.
            host = Host.objects.get(name=name)
        except ObjectDoesNotExist as err:  # If it not exist, no reason to delete it.
            return error_message('host', name, err)
        if addresses:  # If we want to remove associated Addresses. We need to store them into a
            # local variable as we must delete Host before deleting addresses. So we need to keep
            # a trace of them.
            addresses_host = host.addresses.all()
            addresses_delete = []  # addresses we need to delete
            for address in addresses_host:
                addresses_delete.append({
                    'ip': address.ip,
                    'network': address.network,
                    'ns_entry': dns_entry
                })
        if hardware:  # We get the interface, far more easiest as it s a one-to-one relation
            hardware_host = host.interface.hardware
        try:  # Now we can try to remove the Host
            host.delete()
        except IntegrityError as err:  # If for some reason, it s not possible.
            return error_message('host', name, err)
        if addresses_delete is not None:  # Now we can remove addresses
            for address in addresses_delete:
                result = Address.remove(**address)
                if result['status'] != 'done':  # If for some reason, it's not possible
                    return result
        if hardware_host is not None:  # Now we remove the interface
            try:
                host.interface.hardware.delete()
            except IntegrityError as err:
                return error_message('host', name, err)
        return {
            'host': name,
            'status': 'done'
        }

    @staticmethod
    def add(name, address, args=None):
        """
        This is a custom method to add a IP to a host.

        :param name: the host name
        :param address: IP address
        :param args: some optional options
        :return:
        """
        record = name
        if args is not None:
            try:
                record = args['fqdn']
            except KeyError:
                pass
        fqdn = record.split('.', 1)
        ns = fqdn[0]
        domain = fqdn[1]
        ns_entry = {
            'name': ns,
            'domain': domain
        }
        try:
            host = Host.objects.get(name=name)
        except ObjectDoesNotExist as err:
            error_message('host', name, err)
        try:  # get the address
            address = Address.objects.get(ip=address)
            if address.host_set.all() != 0:  # If address is not free, we return a error
                return error_message('host', name, 'Address already used by another host')
        except ObjectDoesNotExist:  # If address not exist, we create if
            network = Address.match_network(ip=address)  # By geting the network associated to it.
            result = Address.create(address, network.name, ns_entry)
            if result['status'] != 'done':  # If something go wrong
                return result
            address = Address.objects.get(ip=address)  # We get the address created
        host.addresses.add(address)  # We add it.
        return {
            'status': 'done',
            'host': name
        }

    @staticmethod
    def get(name):
        """
        This is a custom method to get the dict abstraction of a Host. We get a standard version of
        the abstraction (see show method comment).

        :param name: name of the host
        :return:
        """
        try:
            host = Host.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('host', name, err)
        result = host.show()
        return result

    @staticmethod
    def search(filters=None):
        """
        This is a custom method to get a dict abstraction of all Host on database. We get a
        short version of Host (see show method comment).

        :param filters: a dict of field as QuerySet
        :return:
        """
        if filters is None:  # If no filters, we get all Host
            hosts = Host.objects.all()
        else:  # We suppose filter as been construct outside models class
            hosts = Host.objects.filter(**filters)
        result = []
        for host in hosts:  # We create the dict abstraction
            result.append(host.show(short=True))
        return result
