"""
As this is a django internal template, we disable pylint
"""
# pylint: disable=W0611
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from slam_domain.models import Domain
# Create your tests here.

DOMAIN_OPTIONS_EMPTY = {
    'dns_master': '127.0.0.1'
}

DOMAIN_OPTIONS_FULL = {
    'dns_master': '127.0.0.1',
    'description': 'This is a test',
    'contact': 'ns-master@full.com',
}

EMPTY_DOMAIN_NAME = 'empty.com'
FULL_DOMAIN_NAME = 'full.com'
DELETE_DOMAIN_NAME = 'delete.com'
UPDATE_DOMAIN_NAME = 'update.com'


class DomainTestCase(TestCase):
    def setUp(self) -> None:
        Domain.create(name=EMPTY_DOMAIN_NAME, args=DOMAIN_OPTIONS_EMPTY)
        Domain.create(name=FULL_DOMAIN_NAME, args=DOMAIN_OPTIONS_FULL)
        Domain.create(name=DELETE_DOMAIN_NAME, args=DOMAIN_OPTIONS_EMPTY)
        Domain.create(name=UPDATE_DOMAIN_NAME, args=DOMAIN_OPTIONS_EMPTY)

    def test_domain_get(self):
        empty_com = Domain.objects.get(name=EMPTY_DOMAIN_NAME)
        full_com = Domain.objects.get(name=FULL_DOMAIN_NAME)
        self.assertEqual(empty_com.dns_master, DOMAIN_OPTIONS_EMPTY['dns_master'])
        self.assertIsNone(empty_com.description)
        self.assertIsNone(empty_com.contact)
        self.assertIsNotNone(empty_com.creation_date)
        self.assertEqual(full_com.dns_master, DOMAIN_OPTIONS_FULL['dns_master'])
        self.assertEqual(full_com.description, DOMAIN_OPTIONS_FULL['description'])
        self.assertEqual(full_com.contact, DOMAIN_OPTIONS_FULL['contact'])
        self.assertIsNotNone(full_com.creation_date)

    def test_domain_delete(self):
        Domain.remove(name=DELETE_DOMAIN_NAME)
        with self.assertRaisesMessage(ObjectDoesNotExist, 'Domain matching query does not exist.'):
            Domain.objects.get(name=DELETE_DOMAIN_NAME)

    def test_domain_update(self):
        Domain.update(name=UPDATE_DOMAIN_NAME, args=DOMAIN_OPTIONS_FULL)
        update_com = Domain.objects.get(name=UPDATE_DOMAIN_NAME)
        self.assertEqual(update_com.dns_master, DOMAIN_OPTIONS_FULL['dns_master'])
        self.assertEqual(update_com.description, DOMAIN_OPTIONS_FULL['description'])
        self.assertEqual(update_com.contact, DOMAIN_OPTIONS_FULL['contact'])
