"""
This module provide tools to produce DNS Bind9 configuration. It will put all records on a file
named example.com.db (for example.com) and update SOA serial in a file example.com.soa.db. For some
reason, the serial number should be on its own line with the following format:
    2020010401 ; Serial
"""
# As we use django model that provide objects method which is not visible by pylint, we must
# disable no-member error from pylint
# pylint: disable=E1101
import ipaddress
import os
from datetime import datetime

from django.core.files import locks

from slam_domain.models import Domain, DomainEntry
from slam_network.models import Network


class Bind:
    """
    This class manage Bind9 file production. This only manage name resolution, not reverse IP
    resolution.
    """
    def __init__(self, domain, directory):
        """
        Just a constructor for bind, we need a domain name to produce and a directory where to put
        data generated.

        :param domain: domain name
        :param directory: directory where to put
        """
        self.domain = Domain.objects.get(name=domain)
        self.entries = DomainEntry.objects.filter(domain=self.domain)
        self.directory = directory

    def show(self):
        """
        This method make the rendering and return it as a string. To make git diff easier to read,
        we don't add some timestamp into the file.

        :return:
        """
        result = ''
        for record in self.entries:
            if record.type == 'A':
                for address in record.address_set.all():
                    if address.version() == 6:
                        ns_type = 'AAAA'
                    else:
                        ns_type = 'A'
                    result += '{}    IN {}    {} ; {} - {}\n'.format(record.name, ns_type,
                                                                     address.ip,
                                                                     record.creation_date,
                                                                     record.description)
            elif record.type == 'CNAME':
                for entry in record.entries.all():
                    result += '{}    IN {}    {}.{}. ; {} - {}\n'.format(record.name, record.type,
                                                                         entry.name,
                                                                         entry.domain.name,
                                                                         entry.creation_date,
                                                                         entry.description)
        return result

    def update_soa(self):
        """
        This method update SOA to change Serial number, it s required by bind9 to make modification
        available for other DNS server.

        :return:
        """
        now = datetime.now()
        backup_filename = '{}/{}.soa.{}.old'.format(self.directory, self.domain.name,
                                                    now)
        new_filename = '{}/{}.soa.{}.new'.format(self.directory, self.domain.name,
                                                 now)
        filename = '{}/{}.soa.db'.format(self.directory, self.domain.name)
        try:
            os.rename(filename, backup_filename)
        except FileNotFoundError:
            # If the file not exist, we create a standard SOA file
            result = '$TTL    2H\n'
            result += '@ IN  SOA dns-master.example.com. contact.example.com. (\n'
            result += '          {} ; Serial\n'.format(datetime.now().strftime("%Y%m%d00"))
            result += '          7200          ; Refresh - 2hours\n'
            result += '          1200          ; Retry - 20 minutess\n'
            result += '          3600000       ; Expire - 6 weeks\n'
            result += '          86400 )       ;  Minimum - 24 hours\n'
            backup_file = open(backup_filename, 'w')
            backup_file.write(result)
            backup_file.close()
        new_file = open(new_filename, 'w')
        backup_file = open(backup_filename, 'r')
        for line in backup_file.readlines():
            if 'Serial' in line:
                serial = line.split()[0]
                new_serial = int(serial) + 1
                new_file.write(line.replace(serial, str(new_serial)))
            else:
                new_file.write(line)
        os.rename(new_filename, filename)
        os.remove(backup_filename)

    def save(self):
        """
        This method write on example.com.db file all the records.

        :return:
        """
        filename = '{}/{}.db'.format(self.directory, self.domain.name)
        with open(filename, 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(self.show())
            lock_file.close()
        self.update_soa()


class BindReverse:
    """
    This class manage Bind9 file production. This only reverse IP resolution.
    """
    def __init__(self, network, directory):
        """
        Just a constructor for bind, we need a network name to produce and a directory where to put
        data generated.

        :param network: network name
        :param directory: directory where to put
        """
        self.network = Network.objects.get(name=network)
        ip_network = ipaddress.ip_network('{}/{}'.format(self.network.ip, self.network.prefix))
        if ip_network.prefixlen < 24 and ip_network.version == 4:
            self.subnets = []
            for subnet in ip_network.subnets(new_prefix=24):
                self.subnets.append(subnet)
        else:
            self.subnets = [ip_network]
        self.directory = directory

    def show(self):
        """
        This method make the rendering and return it as a string. To make git diff easier to read,
        we don't add some timestamp into the file.

        :return:
        """
        result = ''
        for address in self.network.addresses():
            for entry in address.ns_entries.all():
                if entry.type == 'PTR':
                    reversed_ip = ipaddress.ip_address(address.ip).reverse_pointer
                    result += '{}    IN {}    {}.{}. ; {} \n'.format(reversed_ip, entry.type,
                                                                     entry.name,
                                                                     entry.domain.name,
                                                                     address.creation_date)
        return result

    def update_soa(self):
        """
        This method update SOA to change Serial number, it s required by bind9 to make modification
        available for other DNS server.

        :return:
        """
        now = datetime.now()
        for network in self.subnets:
            backup_filename = '{}/{}.soa.{}.old'.format(self.directory,
                                                        str(network.network_address).
                                                        replace(':', '.'),
                                                        now)
            new_filename = '{}/{}.soa.{}.new'.format(self.directory,
                                                     str(network.network_address).
                                                     replace(':', '.'),
                                                     now)
            filename = '{}/{}.soa.db'.format(self.directory,
                                             str(network.network_address).
                                             replace(':', '.'))
            try:
                os.rename(filename, backup_filename)
            except FileNotFoundError:
                # If the file not exist, we create a standard SOA file
                result = '$TTL    2H\n'
                result += '@ IN  SOA dns-master.example.com. contact.example.com. (\n'
                result += '          {} ; Serial\n'.format(datetime.now().strftime("%Y%m%d00"))
                result += '          7200          ; Refresh - 2hours\n'
                result += '          1200          ; Retry - 20 minutess\n'
                result += '          3600000       ; Expire - 6 weeks\n'
                result += '          86400 )       ;  Minimum - 24 hours\n'
                backup_file = open(backup_filename, 'w')
                backup_file.write(result)
                backup_file.close()
            new_file = open(new_filename, 'w')
            backup_file = open(backup_filename, 'r')
            for line in backup_file.readlines():
                if 'Serial' in line:
                    item = line.split()
                    serial = item[0]
                    new_serial = int(serial) + 1
                    new_file.write(line.replace(serial, str(new_serial)))
                else:
                    new_file.write(line)
            os.rename(new_filename, filename)
            os.remove(backup_filename)

    def save(self):
        """
        This method write on example.com.db file all the records.

        :return:
        """
        filename = '{}/{}.db'.format(self.directory, self.network.ip.replace(':', '.'))
        with open(filename, 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(self.show())
            lock_file.close()
        self.update_soa()

    def produce(self):
        networks = []
        for network in self.subnets:
            output = ''
            for address in self.network.addresses():
                if ipaddress.ip_address(address.ip) in network:
                    print('    address: {}'.format(address.ip))
                    for entry in address.ns_entries.filter(type='PTR'):
                        reversed_ip = ipaddress.ip_address(address.ip).reverse_pointer
                        output += '{}    IN {}    {}.{}. ; {} \n'.format(reversed_ip, entry.type,
                                                                         entry.name,
                                                                         entry.domain.name,
                                                                         address.creation_date)
            filename = '{}/{}.db'.format(self.directory,
                                         str(network.network_address).replace(':', '.'))
            with open(filename, 'w') as lock_file:
                locks.lock(lock_file, locks.LOCK_EX)
                lock_file.write(self.show())
                lock_file.close()
            networks.append(output)
        self.update_soa()
