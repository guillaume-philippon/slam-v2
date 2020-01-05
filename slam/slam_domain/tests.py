"""
As this is a django internal template, we disable pylint
"""
# pylint: disable=W0611
from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from slam_domain.models import Domain
# Create your tests here.


class DomainTestCase(TestCase):
    def setUp(self) -> None:
        options_empty = {
            'dns_master': '127.0.0.1'
        }
        options_full = {
            'dns_master': '127.0.0.1',
            'description': 'This is a test',
            'contact': 'ns-master@full.com',
        }
        Domain.create(name='empty.com', args=options_empty)
        Domain.create(name='full.com', args=options_full)
        Domain.create(name='delete.com', args=options_empty)
        Domain.create(name='update.com', args=options_empty)

    def test_domain_create(self):
        result = {
            'status': 'done',
            'network': 'create.com'
        }
        # self.assert(Domain.create(name='create.com', args={'dns_master': '127.0.0.1'}),
        #                      result)

    def test_domain_get(self):
        empty_com = Domain.objects.get(name='empty.com')
        full_com = Domain.objects.get(name='full.com')
        self.assertEqual(empty_com.dns_master, '127.0.0.1')
        self.assertIsNone(empty_com.description)
        self.assertIsNone(empty_com.contact)
        self.assertIsNotNone(empty_com.creation_date)
        self.assertEqual(full_com.dns_master, '127.0.0.1')
        self.assertEqual(full_com.description, 'This is a test')
        self.assertEqual(full_com.contact, 'ns-master@full.com')
        self.assertIsNotNone(full_com.creation_date)

    def test_domain_delete(self):
        Domain.remove(name='delete.com')
        with self.assertRaisesMessage(ObjectDoesNotExist, 'Domain matching query does not exist.'):
            Domain.objects.get(name='delete.com')

    def test_domain_update(self):
        options_full = {
            'dns_master': '127.0.0.1',
            'description': 'This is a test',
            'contact': 'ns-master@full.com',
        }
        Domain.update(name='update.com', args=options_full)
        update_com = Domain.objects.get(name='update.com')
        self.assertEqual(update_com.dns_master, '127.0.0.1')
        self.assertEqual(update_com.description, 'This is a test')
        self.assertEqual(update_com.contact, 'ns-master@full.com')
