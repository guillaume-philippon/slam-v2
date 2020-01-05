"""
This module provide some useful tools for GitPython
"""
# As we use django model that provide objects method which is not visible by pylint, we must
# disable no-member error from pylint
# pylint: disable=E1101
import git

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
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    build_repo.git.add('.')
    build_repo.git.commit(m=message)
    build_repo.git.push()
    result = {
        'data': message
    }
    return result
