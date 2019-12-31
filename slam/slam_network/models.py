"""
This module provide model for networks. There are 2 models
 - Network: which represent a IPv6 or IPv4 network
 - Address: which represent a IPv6 or IPv5

As we use django models.Model, pylint fail to find objects method. We must disable pylint
test E1101 (no-member)
"""
# pylint: disable=E1101
import ipaddress

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError

from slam_domain.models import DomainEntry, Domain


class Network(models.Model):
    """
    Network class represent a IPv4 or IPv6 network
     - name: The human reading name of the network
     - description: A short description of the network
     - address: network address (192.168.0.0)
     - prefix: network prefix (/24)
     - gateway: the IP of the network gateway
     - dns_master: The IP of DNS master for reverse resolution (used to push data in production)
     - contact: a contact email for the network
     - dhcp: the IP of DHCP server (used to push data in production)
     - vlan: the VLAN id of the network
    """
    name = models.CharField(max_length=50, unique=True)
    address = models.GenericIPAddressField(unique=True)
    prefix = models.IntegerField(default=24)
    description = models.CharField(max_length=150, default='')
    gateway = models.GenericIPAddressField(blank=True, null=True)
    dns_master = models.GenericIPAddressField(blank=True, null=True)
    dhcp = models.GenericIPAddressField(blank=True, null=True)
    vlan = models.IntegerField(default=1)
    contact = models.EmailField(blank=True, null=True)

    def is_include(self, ip):
        """
        This method check if ip is included on a network
        :param ip: IP address
        :return:
        """
        if ipaddress.ip_address(ip) in ipaddress.ip_network('{}/{}'.format(self.address,
                                                                           self.prefix)):
            return True
        return False

    def addresses(self):
        """
        This method return all addresses which are in the current network.
        :return:
        """
        addresses = Address.objects.all()
        result = []
        for address in addresses:
            if self.is_include(address.ip):
                result.append(address)
        return result

    @staticmethod
    def create(name, address, prefix, description='A short description', gateway=None,
               dns_master=None, dhcp=None, vlan=1, contact=None):
        # pylint: disable=R0913
        """
        This is a custom way to create a network
        :param name: human reading name of the network
        :param address: IPv4 or IPv6 network address
        :param prefix: network prefix
        :param description: A short description of the network
        :param gateway: IP of the network gateway
        :param dns_master: IP of DNS master
        :param dhcp: IP of DHCP server
        :param vlan: VLAN id of the network
        :param contact: a contact email for the network
        :return:
        """
        try:
            network = Network(name=name, address=address, prefix=prefix, description=description,
                              gateway=gateway, dns_master=dns_master, dhcp=dhcp, vlan=vlan,
                              contact=contact)
            network.full_clean()
        except IntegrityError as err:  # In case network already exist
            return {
                'network': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        except ValidationError as err:  # In case of some validation issue w/ fields
            return {
                'network': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        network.full_clean()
        network.save()
        return {
            'network': network.name,
            'status': 'done'
        }

    @staticmethod
    def update(name, description=None, gateway=None, dns_master=None, dhcp=None, vlan=None,
               contact=None):
        # pylint: disable=R0913
        """
        This is a custom method to update value on a existing network
        :param name: human reading name of the network
        :param description: A short description of the network
        :param gateway: The IP of the gateway
        :param dns_master: The IP of DNS master
        :param dhcp: The IP of DHCP server
        :param vlan: The VLAN id
        :param contact: a contact email for the network
        :return:
        """
        try:
            network = Network.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return {
                'network': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        if description is not None:
            network.description = description
        if gateway is not None:
            network.gateway = gateway
        if dns_master is not None:
            network.dns_master = dns_master
        if dhcp is not None:
            network.dhcp = dhcp
        if vlan is not None:
            network.vlan = vlan
        if contact is not None:
            network.contact = contact
        network.full_clean()
        network.save()
        return {
            'network': name,
            'status': 'done'
        }

    @staticmethod
    def remove(name):
        """
        This is a custom method to delete a network. As delete is already used by models.Model,
        we should call it with another name
        :param name: name of network we want delete
        :return:
        """
        try:
            network = Network.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return {
                'network': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        network.delete()
        return {
            'network': name,
            'status': 'done'
        }

    @staticmethod
    def get(name):
        """
        This is a custom method to get all information for a network
        :param name: name of the network
        :return:
        """
        result = {
            'network': name,
        }
        try:
            network = Network.objects.get(name=name)
            result['address'] = network.address
            result['prefix'] = network.prefix
            result['description'] = network.description
            result['gateway'] = network.gateway
            result['dns_master'] = network.dns_master
            result['dhcp'] = network.dhcp
            result['vlan'] = network.vlan
            result['contact'] = network.contact
        except ObjectDoesNotExist as err:
            return {
                'network': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        addresses = network.addresses()
        result_addresses = []
        for address in addresses:
            result_addresses.append({
                'ip': address.ip
            })
        result['addresses'] = result_addresses
        return result

    @staticmethod
    def search(filters=None):
        """
        This is a custom method to get all networks that match the filters
        :param filters: a dict of field / regex
        :return:
        """
        if filters is None:
            networks = Network.objects.all()
        else:
            network = Network.objects.filter(**filters)
        result = []
        for network in networks:
            result.append({
                'network': network.name,
                'address': network.address,
                'prefix': network.prefix,
                'description': network.description
            })
        return result


class Address(models.Model):
    """
    Address class represent a specific address on a network.
     - ip: IPv4 or IPv6 address
     - ns_entries: all other NS entries for this IP (CNAME, A, ...)
    """
    ip = models.GenericIPAddressField(unique=True)
    ns_entries = models.ManyToManyField(DomainEntry)

    @staticmethod
    def create(ip, network, ns_entries=None):
        """
        This is a custom method to create a Address.
        :return:
        """
        try:
            try:
                network_address = Network.objects.get(name=network)
            except ObjectDoesNotExist:
                network_address = None
            if network is not None and not network_address.is_include(ip):
                return {
                    'address': ip,
                    'status': 'failed',
                    'message': 'Address {} not in Network {}/{}'.format(ip, network_address.address,
                                                                        network_address.prefix)
                }
            address = Address(ip=ip)
        except IntegrityError as err:
            return {
                'address': ip,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        except ValidationError as err:
            return {
                'address': ip,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        try:
            address.full_clean()
        except ValidationError as err:
            return {
                'address': ip,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        address.save()
        if ns_entries is not None:
            for ns_entry in ns_entries:
                try:
                    domain = Domain.objects.get(name=ns_entry['domain'])
                    entry = DomainEntry.objects.get(name=ns_entry['name'], domain=domain)
                    address.ns_entries.add(entry)
                except ObjectDoesNotExist as err:
                    return {
                        'address': ip,
                        'status': 'failed',
                        'message': '{}'.format(err)
                    }
        return {
            'address': address.ip,
            'status': 'done'
        }

    @staticmethod
    def include(ip, network, ns_entry, ns_type='A'):
        """
        This is a custom method to add a entry in a address
        :param ip: IP address
        :param network: network
        :param ns_entry: NS entry
        :param ns_type: NS entry type
        :return:
        """
        fqdn = ns_entry.split('.', 1)
        ns = fqdn[0]
        domain = fqdn[1]
        try:
            # network_entry = Network.objects.get(name=network)
            address_entry = Address.objects.get(ip=ip)
            domain_entry = Domain.objects.get(name=domain)
            ns_entry_entry = DomainEntry.objects.get(name=ns, domain=domain_entry, type=ns_type)
        except ObjectDoesNotExist as err:
            return {
                'entry': ns_entry,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        address_entry.ns_entries.add(ns_entry_entry)
        return {
            'entry': ns_entry,
            'status': 'done'
        }

    @staticmethod
    def exclude(ip, network, ns_entry, ns_type='A'):
        """
        This is a custom method to remove a NS entry from address
        :param ip: IP address
        :param network: network
        :param ns_entry: NS entry
        :param ns_type: NS type
        :return:
        """
        fqdn = ns_entry.split('.', 1)
        ns = fqdn[0]
        domain_entry = fqdn[1]
        try:
            # network_entry = Network.objects.get(name=network)
            address_entry = Address.objects.get(ip=ip)
            domain_entry = Domain.objects.get(name=domain_entry)
            ns_entry_entry = DomainEntry.objects.get(name=ns, domain=domain_entry, type=ns_type)
        except ObjectDoesNotExist as err:
            return {
                'entry': ns_entry,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        address_entry.ns_entries.remove(ns_entry_entry)
        return {
            'entry': ns_entry,
            'status': 'done'
        }

    @staticmethod
    def remove(ip, network):
        """
        This is a custom method to delete Address
        :param ip: The IP address we will delete
        :param network: The network name
        :return:
        """
        try:
            try:
                network_address = Network.objects.get(name=network)
            except ObjectDoesNotExist:
                network_address = None
            if network_address is not None and not network_address.is_include(ip):
                return {
                    'address': ip,
                    'status': 'failed',
                    'message': 'Address {} not in Network {}/{}'.format(ip, network_address.address,
                                                                        network_address.prefix)
                }
            address = Address.objects.get(ip=ip)
        except ObjectDoesNotExist as err:
            return {
                'address': ip,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        address.delete()
        return {
            'address': ip,
            'status': 'done'
        }

    @staticmethod
    def get(ip, network):
        """
        This is a custom method to get information about a address
        :param ip: IP address
        :param network: Network
        :return:
        """
        try:
            network = Network.objects.get(name=network)
        except ObjectDoesNotExist as err:
            network = None
        try:
            address = Address.objects.get(ip=ip)
        except ObjectDoesNotExist as err:
            return {
                'address': ip,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        result = {
            'address': address.ip
        }
        result_entries = []
        if address.ns_entries is not None:
            for entry in address.ns_entries.all():
                result_entries.append({
                    'ns': entry.name,
                    'domain': entry.domain.name,
                    'type': entry.type
                })
        result['entries'] = result_entries
        return result

    @staticmethod
    def network(ip):
        """
        This method return the network associated with the address
        :return:
        """
        networks = Network.objects.all()
        for network in networks:
            if network.is_include(ip):
                return network
        return None
