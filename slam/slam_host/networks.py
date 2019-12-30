"""
This module provide some usefull function for Network model usage
"""
from slam_network.models import Network
from slam_host.models import Host

import ipaddress


def get_network_from(ip):
    """
    This function will return a the Network model object associated with the ip.

    :param ip: IP we looking for
    :return:
    """
    networks = Network.objects.all()
    result = None
    for network in networks:
        if network.is_include(ip):
            result = network
    return result


def get_free_ip_from(arg_network):
    """
    This function will return a free IP from the given network

    :param arg_network: Network where we look@
    :return:
    """
    hosts = Host.objects.all()
    result = None
    used = []
    for host in hosts:
        if host.ip_address is not None:
            used.append(ipaddress.ip_address(host.ip_address))
    network = ipaddress.ip_network('{}/{}'.format(arg_network.address, arg_network.prefix))
    for ip in network.hosts():
        if ip not in used:
            result = ip
            break
    return result
