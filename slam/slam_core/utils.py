"""
This module provide some usefull function to avoid copy / paste.
"""
from datetime import datetime
import ipaddress
from django.core.files import locks
import os


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


def bind_domain(domain, data):
    """
    Generate DNS bind9 file

    :param domain:
    :param data:
    :return:
    """
    result = '; SLAM generated file for domain {}. {}\n\n'.format(domain, datetime.now())
    for entry in data['entries']:
        if entry['domain'] == domain and entry['type'] != 'PTR':
            addresses = data['addresses']
            for address in addresses:
                if address['version'] == 6 and entry['type'] == 'A':
                    ns_type = 'AAAA'
                else:
                    ns_type = entry['type']
                address_entry = {
                    'name': entry['name'],
                    'domain': entry['domain'],
                    'type': entry['type']
                }
                if address_entry in address['ns_entries']:
                    result = result + '{}    IN {}    {} ; {}\n'.format(entry['name'], ns_type,
                                                                        address['ip'],
                                                                        entry['description'])
            if entry['type'] == 'CNAME':
                pass
                for sub_entry in entry['entries']:
                    result += '{}    IN {}    {}.{}. ; {}\n'.format(entry['name'],
                                                                    ns_type,
                                                                    sub_entry['name'],
                                                                    sub_entry['domain'],
                                                                    entry['description'])

    return result + '\n\n'


def bind_network(network, data):
    """
    Generate DNS bind9 reverse

    :param network:
    :param data:
    :return:
    """
    result = '; SLAM generated file for network {}. {}\n\n'.format(network, datetime.now())
    for address in data['addresses']:
        for entry in address['ns_entries']:
            if entry['type'] == 'PTR' and address['network'] == network:
                result_address = ipaddress.ip_address(address['ip']).reverse_pointer
                result = result + '{}   IN {}    {}.{}.\n'.format(result_address, entry['type'],
                                                                  entry['name'], entry['domain'])
    return result + '\n\n'


def update_soa(filename):
    """
    Update SOA serial number for Bind9
    :param filename:
    :return:
    """
    backup_filename =  '{}.{}'.format(filename, datetime.now())
    os.rename(filename, backup_filename)
    updated_file = open(filename, 'w')
    source_file = open(backup_filename, 'r')
    for line in source_file.readlines():
        if 'Serial' in line:
            item = line.split()
            new_serial = int(item[0]) + 1
            updated_file.write(line.replace(item[0], str(new_serial)))
        else:
            updated_file.write(line)


def isc_dhcp(network, data):
    """
    Create DHCP entry
    :param network:
    :param data:
    :return:
    """
    for network_data in data['networks']:
        if network_data['name'] == network and network_data['version'] == 6:
            return ''
    result = '# ISC-DHCP configuration for {}. {}\n'.format(network, datetime.now())
    for host in data['hosts']:
        # host host { hardware ethernet 00:11:22:33:44:55; fixed-address host; }
        if host['interface'] != '' and host['network'] == network:
            for interface in data['interfaces']:
                if host['interface'] == interface['mac_address']:
                    interface_host = interface
                    break
            for hardware in data['inventory']:
                if hardware['name'] == interface_host['hardware']:
                    hardware_host = hardware
                    break
            result += '# Buying Date: {}\n'.format(hardware_host['buying_date'])
            result += '# Owner: {}\n'.format(hardware_host['owner'])
            result += 'host {} {{\n'.format(host['name'])
            result += '    hardware ethernet {};\n'.format(host['interface'])
            result += '    fixed-address {};\n'.format(host['name'])
            result += '}}\n'
    return result
