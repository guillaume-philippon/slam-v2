"""
This module provide tools to produce ISC-DHCP configuration. It will put all DHCP entries on a file
named network.conf (for local.conf).
"""
# As we use django model that provide objects method which is not visible by pylint, we must
# disable no-member error from pylint
# pylint: disable=E1101
from datetime import datetime

from django.core.files import locks

from slam_network.models import Network
from slam_host.models import Host


class IscDhcp:
    """
    This class manage ISC-DHCP configuration. It will only provide host configuration, you have to
    include those file on DHCP configuration
    """
    def __init__(self, network, directory):
        """
        This is just a constructor. We need a network and a directory where to put configuration
        file

        :param network: network name
        :param directory: directory where to put data
        """
        self.network = Network.objects.get(name=network)
        self.hosts = Host.objects.all()
        self.directory = directory

    def show(self):
        """
        This method make the rendering and return it as a string. To make git diff easier to read,
        we don't add some timestamp into the file.

        :return:
        """
        if self.network.version() == 6:
            return ''
        result = '# SLAM generated file for network {}. {}\n'.format(self.network.name,
                                                                     datetime.now())
        for host in self.hosts:
            if host.interface is not None and host.dhcp:
                for address in host.addresses.all():
                    if address in self.network.addresses():
                        result_host = 'host {} {{\n'.format(host.name)
                        result_host += '    hardware ethernet {};\n'.format(
                            host.interface.mac_address)
                        result_host += '    fixed-address {};\n'.format(address.ip)
                        result_host += '}\n'
                    if result_host != '':
                        result += result_host
                        result_host = ''
                        break
        return result

    def save(self):
        """
        This method write on example.com.db file all the records.

        :return:
        """
        filename = '{}/{}.conf'.format(self.directory, self.network.name)
        with open(filename, 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(self.show())
            lock_file.close()
