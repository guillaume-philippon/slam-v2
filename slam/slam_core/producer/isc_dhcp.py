"""

"""
from datetime import datetime
from slam_network.models import Network
from slam_host.models import Host

from django.core.files import locks


class IscDhcp:
    """

    """
    def __init__(self, network, dir):
        """

        """
        self.network = Network.objects.get(name=network)
        self.hosts = Host.objects.all()
        self.dir = dir

    def show(self):
        """

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

        :return:
        """
        filename = '{}/{}.conf'.format(self.dir, self.network.name)
        with open(filename, 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(self.show())
            lock_file.close()
