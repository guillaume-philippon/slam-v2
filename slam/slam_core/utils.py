"""
This module provide some usefull function to avoid copy / paste.
"""
from datetime import datetime
from django.core.files import locks


def error_message(plugin, value, message):
    """
    This function return a dict construction for error message

    :param plugin: plugin name
    :param value: value of plugin name
    :param message: error message
    :return:
    """
    result = dict()
    result[plugin] = value
    result['status'] = 'failed'
    result['message'] = '{}'.format(message)
    return result


def write_file(filename, contents):
    """

    :param filename:
    :param contents:
    :return:
    """
    with open(filename, 'w') as lock_file:
        locks.lock(lock_file, locks.LOCK_EX)
        lock_file.write(contents)
        lock_file.close()


def isc_dhcp(network_name, data):
    """
    Create DHCP entry
    :param network:
    :param data:
    :return:
    """
    for network_data in data['networks']:
        if network_data['name'] == network_name and network_data['version'] == 6:
            return ''
    result = '# ISC-DHCP configuration for {}. {}\n'.format(network_name, datetime.now())
    for host in data['hosts']:
        # host host { hardware ethernet 00:11:22:33:44:55; fixed-address host; }
        if len(host['interface']) != 0:
            result_host = 'host {} {{\n'.format(host['name'])
            result_host += '    hardware ethernet {};\n'.format(host['interface']['mac_address'])
            result_host += '    fixed-address {};\n'.format(host['name'])
            result_host += '}}\n'
        result += result_host
    return result + '\n\n'
