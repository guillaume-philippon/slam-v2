"""

"""
import git

from slam_network.models import Network
from slam_domain.models import Domain

from slam_core.producer.bind import BindReverse, Bind

PRODUCER_DIRECTORY = './build'


def commit():
    """

    :return:
    """
    for domain in Domain.objects.all():
        cur_domain = Bind(domain.name, PRODUCER_DIRECTORY + '/bind')
        cur_domain.save()
    for network in Network.objects.all():
        cur_network = BindReverse(network.name, PRODUCER_DIRECTORY + '/bind')
        cur_network.save()
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    result = build_repo.git.diff()
    return result


def publish(message='This is the default comment'):
    """

    :return:
    """
    build_repo = git.Repo(PRODUCER_DIRECTORY)
    build_repo.git.add('.')
    build_repo.git.commit(m=message)
    build_repo.git.push()
    return message
