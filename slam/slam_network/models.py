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

from slam_core.utils import error_message, name_validator
from slam_domain.models import DomainEntry, Domain
from slam_network.exceptions import NetworkFull


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
    name = models.CharField(max_length=50, unique=True, validators=[name_validator])
    ip = models.GenericIPAddressField(unique=True)
    prefix = models.IntegerField(default=24)
    description = models.CharField(max_length=150, default='')
    gateway = models.GenericIPAddressField(blank=True, null=True)
    dns_master = models.GenericIPAddressField(blank=True, null=True)
    dhcp = models.GenericIPAddressField(blank=True, null=True)
    vlan = models.IntegerField(default=1)
    contact = models.EmailField(blank=True, null=True)

    def show(self, key=False, short=False):
        if key:
            result = {
                'name': self.name
            }
        elif short:
            addresses_used = len(self.addresses())
            addresses_total = ipaddress.ip_network('{}/{}'.format(self.ip,
                                                                  self.prefix)).num_addresses
            result = {
                'name': self.name,
                'address': self.ip,
                'prefix': self.prefix,
                'version': ipaddress.ip_address(self.ip).version,
                'description': self.description,
                'used_addresses': addresses_used,
                'total': addresses_total
            }
        else:
            result_addresses = []
            for address in self.addresses():
                result_addresses.append(address.show(short=True))
            addresses_used = len(self.addresses())
            addresses_total = ipaddress.ip_network('{}/{}'.format(self.ip,
                                                                  self.prefix)).num_addresses
            result = {
                'name': self.name,
                'address': self.ip,
                'prefix': self.prefix,
                'version': ipaddress.ip_address(self.ip).version,
                'description': self.description,
                'gateway': self.gateway,
                'dns_master': self.dns_master,
                'dhcp': self.dhcp,
                'vlan': self.vlan,
                'contact': self.contact,
                'used_addresses': addresses_used,
                'total': addresses_total,
                'addresses': result_addresses
            }
        return result

    def is_include(self, ip):
        """
        This method check if ip is included on a network
        :param ip: IP address
        :return:
        """
        address = ipaddress.ip_address(ip)
        network = ipaddress.ip_network('{}/{}'.format(self.ip, self.prefix))
        if address.version == network.version and address in network:
            return True
        return False

    def addresses(self):
        """
        This method return all addresses which are in the current network.
        :return:
        """
        result = self.address_set.all()
        return result

    def get_free_ip(self):
        """

        :return:
        """
        network = ipaddress.ip_network('{}/{}'.format(self.ip, self.prefix))
        addresses = []
        for address in self.addresses():
            addresses.append(ipaddress.ip_address(address.ip))
        for result_address in network.hosts():
            if result_address not in addresses:
                return result_address
        raise NetworkFull()

    def version(self):
        """

        :return:
        """
        return ipaddress.ip_network('{}/{}'.format(self.ip, self.prefix)).version

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
            network = Network(name=name, ip=address, prefix=prefix, description=description,
                              gateway=gateway, dns_master=dns_master, dhcp=dhcp, vlan=vlan,
                              contact=contact)
            network.full_clean()
        except (IntegrityError, ValidationError) as err:  # In case network already exist
            return error_message('network', name, err)
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
            return error_message('network', name, err)
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
        try:
            network.full_clean()
        except ValidationError as err:
            return error_message('network', name, err)
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
            network.delete()
        except (ObjectDoesNotExist, IntegrityError) as err:
            return error_message('network', name, err)
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
        try:
            network = Network.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('network', name, err)
        result = network.show()
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
            networks = Network.objects.filter(**filters)
        result = []
        for network in networks:
            result.append(network.show(short=True))
        return result


class Address(models.Model):
    """
    Address class represent a specific address on a network.
     - ip: IPv4 or IPv6 address
     - ns_entries: all other NS entries for this IP (CNAME, A, ...)
    """
    ip = models.GenericIPAddressField(unique=True)
    ns_entries = models.ManyToManyField(DomainEntry)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    network = models.ForeignKey(Network, on_delete=models.PROTECT)

    def show(self, key=False, short=True):
        """

        :param key:
        :param short:
        :return:
        """
        if key:
            result = {
                'ip': self.ip,
            }
        elif short:
            result_entries = []
            for entry in self.ns_entries.all():
                result_entries.append(entry.show(key=True))
            result = {
                'ip': self.ip,
                'ns_entries': result_entries,
                'creation_date': self.creation_date,
                'network': self.network.show(key=True)
            }
        else:
            result_entries = []
            for entry in self.ns_entries.all():
                result_entries.append(entry.show(short=True))
            result = {
                'ip': self.ip,
                'ns_entries': result_entries,
                'creation_date': self.creation_date,
                # 'network': self.network.show(short=True)
            }
        return result

    def version(self):
        """

        :return:
        """
        return ipaddress.ip_address(self.ip).version

    @staticmethod
    def create(ip, network, ns_entry=None):
        """
        This is a custom method to create a Address.

        :param ip:
        :param network:
        :param ns_entry:
        :return:
        """
        try:
            try:
                network_address = Network.objects.get(name=network)
            except ObjectDoesNotExist as err:
                return error_message('address', ip, err)
            if network_address is not None and not network_address.is_include(ip):
                return error_message('address', ip, 'Address {} not in Network {}/{}'.format(
                    ip, network_address.address, network_address.prefix))
            address = Address(ip=ip, network=network_address)
            address.full_clean()
        except (IntegrityError, ValueError, ValidationError) as err:
            return error_message('address', ip, err)
        address.save()
        if ns_entry is not None:
            try:
                domain = Domain.objects.get(name=ns_entry['domain'])
            except ObjectDoesNotExist as err:
                return error_message('address', ip, err)
            try:
                entry = DomainEntry.objects.get(name=ns_entry['name'], domain=domain, type='A')
            except ObjectDoesNotExist as err:
                # If NS entry not exist, we create it.
                result = DomainEntry.create(name=ns_entry['name'], domain=ns_entry['domain'])
                entry = DomainEntry.objects.get(name=ns_entry['name'], domain=domain, type='A')
                if result['status'] != 'done':
                    return result
            try:
                entry_ptr = DomainEntry.objects.get(name=ns_entry['name'], domain=domain,
                                                    type='PTR')
            except ObjectDoesNotExist:
                result = DomainEntry.create(name=ns_entry['name'], domain=ns_entry['domain'],
                                            ns_type='PTR')
                if result['status'] != 'done':
                    return result
                entry_ptr = DomainEntry.objects.get(name=ns_entry['name'], domain=domain,
                                                    type='PTR')
            address.ns_entries.add(entry)
            address.ns_entries.add(entry_ptr)
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
            network_entry = Network.objects.get(name=network)
            if network_entry is not None and not network_entry.is_include(ip):
                return error_message('entry', ns_entry, 'Address {} not in Network {}/{}'.format(
                    ip, network_entry.address, network_entry.prefix))
            address_entry = Address.objects.get(ip=ip)
            domain_entry = Domain.objects.get(name=domain)
            ns_entry_obj = DomainEntry.objects.get(name=ns, domain=domain_entry, type=ns_type)
            if ns_type == 'PTR' and len(ns_entry_obj.address_set.all()) != 0:
                return error_message('entry', ip, 'PTR record is used')
        except ObjectDoesNotExist as err:
            return error_message('entry', ns_entry, err)
        address_entry.ns_entries.add(ns_entry_obj)
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
            return error_message('entry', ns_entry, err)
        address_entry.ns_entries.remove(ns_entry_entry)
        return {
            'entry': ns_entry,
            'status': 'done'
        }

    @staticmethod
    def remove(ip, network, ns_entry=True):
        """
        This is a custom method to delete Address
        :param ip: The IP address we will delete
        :param network: The network name
        :param ns_entry: If true, we also remove PTR and A resolution name (default True)
        :return:
        """
        try:
            try:
                network_address = Network.objects.get(name=network)
            except ObjectDoesNotExist:
                network_address = None
            if network_address is not None and not network_address.is_include(ip):
                return error_message('address', ip, 'Address {} not in Network {}/{}'.format(
                    ip, network_address.address, network_address.prefix))
            address = Address.objects.get(ip=ip)
            try:
                entry_ptr = address.ns_entries.get(type='PTR')
            except ObjectDoesNotExist:
                entry_ptr = None
            try:
                entry_a = address.ns_entries.get(type='A')
            except ObjectDoesNotExist:
                entry_a = None
            address.delete()
        except (ObjectDoesNotExist, IntegrityError) as err:
            return error_message('address', ip, err)
        if ns_entry:
            if entry_ptr is not None:
                try:
                    if len(entry_ptr.address_set.all()) == 0:
                        # We only delete PTR if no other address use it. (ie it s a orphan entry)
                        entry_ptr.delete()
                except (IntegrityError, ObjectDoesNotExist) as err:
                    return error_message('address', ip, err)
            if entry_a is not None:
                try:
                    if len(entry_a.address_set.all()) == 0:
                        # We only delete A if no other address use it. (ie it s a orphan entry)
                        entry_a.delete()
                except (IntegrityError, ObjectDoesNotExist) as err:
                    return error_message('address', ip, err)
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
            return error_message('address', ip, err)
        result = address.show()
        return result

    @staticmethod
    def search(filters=None):
        """
        This is a custom method to get all networks that match the filters
        :param filters: a dict of field / regex
        :return:
        """
        if filters is None:
            addresses = Address.objects.all()
        else:
            addresses = Address.objects.filter(**filters)
        result = []
        for address in addresses:
            result.append(address.show(short=True))
        return result

    @staticmethod
    def match_network(ip):
        """
        This method return the network associated with the address
        :return:
        """
        networks = Network.objects.all()
        for network in networks:
            if network.is_include(ip):
                return network
        return None
