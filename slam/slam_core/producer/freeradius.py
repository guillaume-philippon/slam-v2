"""
This module provide tools to produce freeradius configuration. A freeradius file look like

    00:11:22:33:44:55 Cleartext-Password := 00:11:22:33:44:55
        Tunnel-Type = VLAN,
        Tunnel-Medium-Type = IEEE-802,
        Tunnel-Private-Group-Id = vlan-id
    DEFAULT Auth-Type := Reject
        Reply-Message = "Pas d'autorisation"
"""
# As we use django model that provide objects method which is not visible by pylint, we must
# disable no-member error from pylint
# pylint: disable=E1101
from django.core.files import locks


class FreeRadius:
    """
    This class manage freeradius configuration
    """
    def __init__(self, hosts, directory):
        """
        This is just a constructor. We just need a directory to put data

        :param directory: directory where to put data
        """
        self.hosts = hosts
        self.directory = directory

    def show(self):
        """
        This method make the rendering and return it as a string. To make git diff easier to read,
        we don't add some timestamp into the file.

        :return:
        """
        result = ''
        for host in self.hosts:
            if host.interface is not None:
                result += '{} Cleartext-Password := {}\n'.format(host.interface.mac_address,
                                                                 host.interface.mac_address)
                result += '    Tunnel-Type = VLAN,\n'
                result += '    Tunnel-Medium-Type = IEEE-802,\n'
                result += '    Tunnel-Private-Group-Id = {}\n'.format(host.network.vlan)
        result += 'DEFAULT Auth-Type := Reject\n'
        result += '    Reply-Message = "No authorisation"\n'
        return result

    def save(self):
        """
        This method write on example.com.db file all the records.

        :return:
        """
        filename = '{}/users'.format(self.directory)
        with open(filename, 'w') as lock_file:
            locks.lock(lock_file, locks.LOCK_EX)
            lock_file.write(self.show())
            lock_file.close()
