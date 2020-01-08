"""
This module provide some useful tools for GitPython
"""
# As we use django model that provide objects method which is not visible by pylint, we must
# disable no-member error from pylint
# pylint: disable=E1101
import git
from paramiko import SSHClient

from slam_network.models import Network
from slam_domain.models import Domain
from slam_core.producer.bind import BindReverse, Bind
from slam_core.producer.isc_dhcp import IscDhcp
from slam_core.producer.freeradius import FreeRadius

PRODUCER_DIRECTORY = './build'


def commit():
    """
    This method trig a git commit for DNS/DHCP and freeradius

    :return:
    """
    for domain in Domain.objects.all():
        domain_bind = Bind(domain.name, PRODUCER_DIRECTORY + '/bind')
        domain_bind.save()
    for network in Network.objects.all():
        network_bind = BindReverse(network.name, PRODUCER_DIRECTORY + '/bind')
        network_bind.save()
        network_isc_dhcp = IscDhcp(network.name, PRODUCER_DIRECTORY + '/isc-dhcp')
        network_isc_dhcp.save()
    freeradius = FreeRadius(PRODUCER_DIRECTORY + '/freeradius')
    freeradius.save()
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    result = {
        'data': build_repo.git.diff()
    }
    return result


def diff():
    """
    This function trig a git diff command to let user see differences before pushing data

    :return:
    """
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    result = {
        'data': build_repo.git.diff()
    }
    return result


def publish(message='This is the default comment'):
    """
    This function trig a git push command to make data available for production

    :return:
    """
    dns_servers = []
    dhcp_servers = []
    freeradius_servers = []
    result = ''
    domains = Domain.objects.all()
    networks = Network.objects.all()
    for domain in domains:  # We get DNS servers
        if domain.dns_master is not None:
            dns_servers.append(domain.dns_master)
    for network in networks:  # We get DNS, DHCP servers
        if network.dns_master is not None:
            dns_servers.append(network.dns_master)
        if network.dhcp is not None:
            dhcp_servers.append(network.dhcp)
    # We commit & push data
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    build_repo.git.add('.')
    build_repo.git.commit(m=message)
    build_repo.git.push()

    # We create a ssh client objects
    client = SSHClient()
    client.load_system_host_keys()
    for dns_server in dns_servers:  # And we start SLAM sync. scripts for each domains
        client.connect(hostname=dns_server, username='root')
        stdin, stdout, stderr = client.exec_command('/usr/bin/slam-bind')
        for line in stdout.readlines():
            result += 'DNS pull {}'.format(dns_server)
            result += '{}\n'.format(line)
        for line in stderr.readlines():
            result += '{}\n'.format(line)
    for dhcp_server in dhcp_servers:
        client.connect(hostname=dns_server, username='root')
        stdin, stdout, stderr = client.exec_command('/usr/bin/slam-isc-dhcp')
    for line in stdout.readlines():
        result += 'DHCP pull {}'.format(dhcp_server)
        result += '{}\n'.format(line)
    for line in stderr.readlines():
        result += '{}\n'.format(line)
    result_json = {
        'data': result
    }
    return result_json
