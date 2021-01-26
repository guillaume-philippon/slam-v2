"""
This module provide some useful tools for GitPython
"""
# As we use django model that provide objects method which is not visible by pylint, we must
# disable no-member error from pylint
# pylint: disable=E1101
from datetime import datetime
import git
from paramiko import SSHClient, AutoAddPolicy

from slam_network.models import Network
from slam_domain.models import Domain
from slam_host.models import Host
from slam_core.producer.bind import BindReverse, Bind
from slam_core.producer.isc_dhcp import IscDhcp
from slam_core.producer.freeradius import FreeRadius

PRODUCER_DIRECTORY = './build'
PRODUCER_SSH_DIR = './ssh'


def commit():
    """
    This method trig a git commit for DNS/DHCP and freeradius

    :return:
    """
    domains = Domain.objects.all()
    hosts = Host.objects.all()
    networks = Network.objects.all()
    print('#### DOMAINS ####')
    for domain in domains:
        print('{}    BEGIN    {}'.format(domain.name, datetime.now()))
        domain_bind = Bind(domain, PRODUCER_DIRECTORY + '/bind')
        domain_bind.save()
        print('{}    END      {}'.format(domain.name, datetime.now()))
    for network in networks:
        print('#### NETWORK BIND ####')
        print('{}   BEGIN   {}'.format(network.name, datetime.now()))
        network_bind = BindReverse(network, PRODUCER_DIRECTORY + '/bind')
        network_bind.produce()
        print('{}   END     {}'.format(network.name, datetime.now()))
        print('#### NETWORK DHCP ####')
        print('{}   BEGIN   {}'.format(network.name, datetime.now()))
        network_isc_dhcp = IscDhcp(network, hosts, PRODUCER_DIRECTORY + '/isc-dhcp')
        network_isc_dhcp.save()
        print('{}   END     {}'.format(network.name, datetime.now()))
    print('#### FREERADIUS ####')
    print('   BEGIN   {}'.format(datetime.now()))
    freeradius = FreeRadius(hosts, PRODUCER_DIRECTORY + '/freeradius')
    freeradius.save()
    print('   BEGIN   {}'.format(datetime.now()))
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
    servers = []
    result = ''
    domains = Domain.objects.all()
    networks = Network.objects.all()
    for domain in domains:  # We get DNS servers
        if domain.dns_master is not None and\
                domain.dns_master not in servers:
            servers.append(domain.dns_master)
    for network in networks:  # We get DNS, DHCP servers
        if network.dns_master is not None and\
                network.dns_master not in servers:
            servers.append(network.dns_master)
        if network.dhcp is not None and\
                network.dhcp not in servers:
            servers.append(network.dhcp)
        if network.radius is not None and\
                network.radius not in servers:
            servers.append(network.radius)
    # We commit & push data
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    build_repo.git.add('.')
    try:  # If there are no modification, PythonGit raise a exception.
        build_repo.git.commit(m=message)
    except git.GitCommandError:
        pass
    build_repo.git.push()

    # We create a ssh client objects
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    for server in servers:  # And we start SLAM sync. scripts for each domains
        client.connect(hostname=server, username='root', key_filename='ssh/id_rsa')
        _, stdout, stderr = client.exec_command('/usr/local/bin/slam-agent')
        result += 'Reload config. on {}'.format(server)
        for line in stdout.readlines():
            result += '{}\n'.format(line)
        result += 'stderr on {}'.format(server)
        for line in stderr.readlines():
            result += '{}\n'.format(line)
        client.close()
    result_json = {
        'data': result
    }
    return result_json
