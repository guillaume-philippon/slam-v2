"""
This module provide some usefull function to avoid copy / paste.
"""
from datetime import datetime
import ipaddress
from django.core.files import locks
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files import File

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


def bind_domain(domain_name, data):
    """
    Generate DNS bind9 file

    :param domain:
    :param data:
    :return:
    """
    result = '; BEGIN SLAM generated file for domain {}. {}\n\n'.format(domain_name, datetime.now())
    for domain in data['domains']:
        if domain_name == domain['name']:
            for record in domain['entries']:
                if record['type'] == 'CNAME':
                    for sub_entry in record['entries']:
                        result_record = '{}    IN {}    {}.\n'.format(
                            record['name'],
                            record['type'],
                            sub_entry['name']
                        )
                elif record['type'] == 'A':
                    for address in record['addresses']:
                        if ipaddress.ip_address(address['ip']).version == 6:
                            ns_type = 'AAAA'
                        else:
                            ns_type = record['type']
                        result_record = '{}    IN {}    {}\n'.format(
                            record['name'],
                            ns_type,
                            address['ip'],
                        )
                result += result_record
    result += '; END SLAM generated file for domain {}. {}\n\n'.format(domain_name, datetime.now())
    return result + '\n\n'


def bind_network(network_name, data):
    """
    Generate DNS bind9 reverse

    :param network:
    :param data:
    :return:
    """
    result = '; SLAM generated file for network {}. {}\n\n'.format(network_name, datetime.now())
    for network in data['networks']:
        if network['name'] == network_name:
            print(network)
            for address in network['addresses']:
                for ip_address in data['addresses']:
                    if address['ip'] == ip_address['ip']:
                        for record in ip_address['ns_entries']:
                            if record['type'] == 'PTR':
                                result_record = '{}    IN {}    {}\n'.format(
                                    ipaddress.ip_address(address['ip']),
                                    record['type'],
                                    record['name']
                                )
                                result += result_record
    return result + '\n\n'


def update_soa(filename):
    """
    Update SOA serial number for Bind9
    :param filename:
    :return:
    """
    current_date = datetime.now()
    backup_filename = '{}.old.{}'.format(filename, current_date)
    new_filename = '{}.new.{}'.format(filename, current_date)
    os.rename(filename, backup_filename)
    updated_file = open(new_filename, 'w')
    source_file = open(backup_filename, 'r')
    for line in source_file.readlines():
        if 'Serial' in line:
            item = line.split()
            new_serial = int(item[0]) + 1
            updated_file.write(line.replace(item[0], str(new_serial)))
        else:
            updated_file.write(line)
    os.rename(new_filename, filename)


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
