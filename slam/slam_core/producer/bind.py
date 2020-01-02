"""

"""
import ipaddress
import os
from datetime import datetime

from django.core.files import locks

from slam_domain.models import Domain, DomainEntry
from slam_network.models import Network


class Bind:
    """
    This class manage Bind 9 configuration
    """
    def __init__(self, domain, dir):
        """

        """
        self.domain = Domain.objects.get(name=domain)
        self.entries = DomainEntry.objects.filter(domain=self.domain)
        self.dir = dir

    def show(self):
        """

        :return:
        """
        result = '; SLAM generated file for domain {} - {}\n'.format(self.domain.name,
                                                                     datetime.now())
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

        :return:
        """
        now = datetime.now()
        backup_filename = '{}/{}.{}.old'.format(self.dir, self.domain.name,
                                                now)
        new_filename = '{}/{}.{}.new'.format(self.dir, self.domain.name,
                                             now)
        filename = '{}/{}.db'.format(self.dir, self.domain.name)
        os.rename(filename, backup_filename)
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

        :return:
        """
        filename = '{}/{}.db'.format(self.dir, self.domain.name)
        with open(filename, 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(self.show())
            lock_file.close()
        self.update_soa()


class BindReverse:
    def __init__(self, network, dir):
        """

        """
        self.network = Network.objects.get(name=network)
        self.dir = dir

    def show(self):
        """

        :return:
        """
        result = '; SLAM generated file for domain {} - {}\n'.format(self.network.name,
                                                                     datetime.now())
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

        :return:
        """
        now = datetime.now()
        backup_filename = '{}/{}.soa.{}.old'.format(self.dir, self.network.name,
                                                    now)
        new_filename = '{}/{}.soa.{}.new'.format(self.dir, self.network.name,
                                                 now)
        filename = '{}/{}.soa.db'.format(self.dir, self.network.name)
        os.rename(filename, backup_filename)
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

        :return:
        """
        filename = '{}/{}.db'.format(self.dir, self.network.name)
        with open(filename, 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(self.show())
            lock_file.close()
        self.update_soa()

