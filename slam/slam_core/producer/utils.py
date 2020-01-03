"""

"""
import git

from slam_network.models import Network
from slam_domain.models import Domain

from slam_core.producer.bind import BindReverse, Bind
from slam_core.producer.isc_dhcp import IscDhcp

PRODUCER_DIRECTORY = './build'


def commit():
    """

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

    build_repo = git.Repo(PRODUCER_DIRECTORY)
    result = {
        'data': build_repo.git.diff()
    }
    return result


def diff():
    """

    :return:
    """
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    result = {
        'data': build_repo.git.diff()
    }
    return result


def publish(message='This is the default comment'):
    """

    :return:
    """
    ssh_cmd = 'ssh -i conf/id_rsa'
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    build_repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd)
    build_repo.git.add('.')
    build_repo.git.commit(m=message)
    build_repo.git.push()
    result = {
        'data': message
    }
    return result
