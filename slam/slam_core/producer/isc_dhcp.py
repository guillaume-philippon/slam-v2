"""
This module provide tools to produce ISC-DHCP configuration. It will put all DHCP entries on a file
named network.conf (for local.conf).
"""
# As we use django model that provide objects method which is not visible by pylint, we must
# disable no-member error from pylint
# pylint: disable=E1101
from django.core.files import locks


class IscDhcp:
    """
    This class manage ISC-DHCP configuration. It will only provide host configuration, you have to
    include those file on DHCP configuration
    """
    def __init__(self, network, hosts, directory):
        """
        This is just a constructor. We need a network and a directory where to put configuration
        file

        :param network: network name
        :param directory: directory where to put data
        """
        self.network = network
        self.hosts = hosts
        self.directory = directory

    def show(self):
        """
        This method make the rendering and return it as a string. To make git diff easier to read,
        we don't add some timestamp into the file.

        :return:
        """
        if self.network.version() == 6:
            return '', ''
        result_fixed = ''
        result_dynamic = 'class "dynamic-{}" {{ match hardware; }}\n'.format(self.network.name)
        for host in self.hosts:
            if host.interface is not None and host.dhcp:
                addresses = host.addresses.filter(network=self.network).count()
                if addresses != 0:
                    result_host = 'host {} {{\n'.format(host.name)
                    result_host += '    hardware ethernet {};\n'.format(
                        host.interface.mac_address)
                    result_host += '    fixed-address {};\n'.format(host.name)
                    result_host += '}\n'
                    result_fixed += result_host
                elif host.network == self.network:
                    result_dynamic += 'subclass "dynamic-{}" {};\n'.format(self.network.name,
                                                                           host.interface.
                                                                           mac_address)
        return result_fixed, result_dynamic

    def save(self):
        """
        This method write on example.com.db file all the records.

        :return:
        """
        filename = '{}/{}.conf'.format(self.directory, self.network.name)
        fixed, dynamic = self.show()
        with open(filename, 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(fixed)
            lock_file.close()
        with open('{}-dynamic'.format(filename), 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(dynamic)
            lock_file.close()
