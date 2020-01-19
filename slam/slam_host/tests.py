"""
As this is a django internal template, we disable pylint
"""
# pylint: disable=W0611
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from slam_domain.models import Domain, DomainEntry
from slam_network.models import Network, Address
from slam_host.models import Host

DOMAIN_EXAMPLE_OPTIONS = {
    'dns_master': '127.0.0.1'
}

DOMAIN_EXAMPLE_NAME = 'example.com'

NETWORK_OPTIONS = {
    'name': 'net.example',
    'ip': '192.168.0.0',
    'prefix': '24'
}

RETURN_NO_ADDRESS_OR_NETWORK = {
    'host': 'no-address-or-network.example.com',
    'message': 'Integrity error Address or Network should be provide',
    'status': 'failed'
}

RETURN_NAME_EXIST = {
    'host': 'dynamic.example.com',
    'message': '{\'name\': [\'Host with this Name already exists.\']}',
    'status': 'failed'
}

RETURN_ADDRESS_USED = {
    'host': 'address-used.example.com',
    'message': 'Address is used by another host',
    'status': 'failed'
}

RETURN_HOST_DELETE = {
    'host': 'dynamic.example.com',
    'status': 'done'
}

RETURN_HOST_DELETE_NOT_EXIST = {
    'host': 'dynamic.example.com',
    'message': 'Host matching query does not exist.',
    'status': 'failed'
}

ADDRESS_NOT_EXIST = {
    'address': '192.168.0.1',
    'message': 'Address matching query does not exist.',
    'status': 'failed'
}

RECORD_NOT_EXIST_A = {
    'entry': 'dynamic.example.com A',
    'message': 'DomainEntry matching query does not exist.',
    'status': 'failed'
}

RECORD_NOT_EXIST_PTR = {
    'entry': 'dynamic.example.com PTR',
    'message': 'DomainEntry matching query does not exist.',
    'status': 'failed'
}


class DomainTestCase(TestCase):
    def setUp(self) -> None:
        Domain.create(name=DOMAIN_EXAMPLE_NAME, args=DOMAIN_EXAMPLE_OPTIONS)
        Network.create(name=NETWORK_OPTIONS['name'],
                       address=NETWORK_OPTIONS['ip'],
                       prefix=NETWORK_OPTIONS['prefix'])

        # We try to create a host w/ network, should take first IP in range
        result = Host.create(name='dynamic.example.com', network='net.example')
        self.assertEqual(result['status'], 'done')
        self.assertEqual(result['addresses'][0]['ip'], '192.168.0.1')
        self.assertEqual(result['network']['name'], NETWORK_OPTIONS['name'])

        # We try to create a host w/ fixed IP address
        result = Host.create(name='fixed.example.com', address='192.168.0.2')
        self.assertEqual(result['status'], 'done')
        self.assertEqual(result['addresses'][0]['ip'], '192.168.0.2')
        self.assertEqual(result['network']['name'], NETWORK_OPTIONS['name'])

    def test_host_create(self):
        # We try to create a host w/o network, it s forbidden
        result = Host.create(name='no-address-or-network.example.com')
        self.assertDictEqual(result, RETURN_NO_ADDRESS_OR_NETWORK)

        # We try to create a host w/ the same name. It s forbidden
        result = Host.create(name=RETURN_NAME_EXIST['host'], network='net.example')
        self.assertDictEqual(result, RETURN_NAME_EXIST)

        # We try to create a host w/ fixed IP
        result = Host.create(name='address-used.example.com', address='192.168.0.1')
        self.assertDictEqual(result, RETURN_ADDRESS_USED)

    def test_host_delete(self):
        # We try to delete a host
        result = Host.remove(name='dynamic.example.com')
        self.assertDictEqual(result, RETURN_HOST_DELETE)
        # If host is correctly deleted, IP address should be removed
        result = Address.get(ip='192.168.0.1', network='net.example')
        self.assertDictEqual(result, ADDRESS_NOT_EXIST)
        # If host is correctly deleted, A and PTR record should be deleted
        result = DomainEntry.get(name='dynamic', domain='example.com', ns_type='A')
        self.assertDictEqual(result, RECORD_NOT_EXIST_A)
        result = DomainEntry.get(name='dynamic', domain='example.com', ns_type='PTR')
        self.assertDictEqual(result, RECORD_NOT_EXIST_PTR)

        # We try to delete a host which not exist
        result = Host.remove(name='dynamic.example.com')
        self.assertDictEqual(result, RETURN_HOST_DELETE_NOT_EXIST)
