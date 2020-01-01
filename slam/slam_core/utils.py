"""
This module provide some usefull function to avoid copy / paste.
"""
from datetime import datetime
import ipaddress
from django.core.files import locks
import os
import time
import tempfile


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
                if address['type'] == 6 and entry['type'] == 'A':
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
            if entry['type'] == 'PTR':
                result_address = ipaddress.ip_address(address['ip']).reverse_pointer
                result = result + '{}   IN {}    {}.{}.\n'.format(result_address, entry['type'],
                                                                  entry['name'], entry['domain'])
    return result + '\n\n'


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
