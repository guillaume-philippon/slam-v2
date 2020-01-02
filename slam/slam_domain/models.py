"""
This module provide model for domains. There are 2 models
 - Domain: which represent a DNS domain like example.com
 - DomainEntry: which represent a named entry like www.example.com

As we use meta class from django that not require any public method, we disable pylint
for R0903 (too-few-public-methods)
As we use models from django that make pylint difficult to know embeded method we must disable
E1101 (no-member)
"""
# pylint: disable=R0903, E1101
from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError

from slam_core.utils import error_message


class Domain(models.Model):
    """
    Domain class represent a fqdn domain like example.com
    - name: immutable name of the domain (example.com)
    - description: a short description of the domain
    - dns_master: IP of DNS master (used to push data in production)
    - contact: a contact email for the domain
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=120, blank=True, null=True)
    dns_master = models.GenericIPAddressField()
    contact = models.EmailField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)

    def show(self, key=False, short=False):
        """

        :param key:
        :param short:
        :return:
        """
        if key:
            result = {
                'name': self.name
            }
        elif short:
            result_entries = []
            entries = DomainEntry.objects.filter(domain=self)
            for entry in entries:
                result_entries.append(entry.show(key=True))
            result = {
                'name': self.name,
                'description': self.description,
                'entries': result_entries
            }
        else:
            result_entries = []
            entries = DomainEntry.objects.filter(domain=self)
            for entry in entries:
                result_entries.append(entry.show(key=True))
            result = {
                'name': self.name,
                'description': self.description,
                'contact': self.contact,
                'creation_date': self.creation_date,
                'entries': result_entries
            }
        return result

    @staticmethod
    def create(name, dns_master, description=None, contact=None):
        """
        A custom way to create a domain.

        :param name: the DNS name
        :param dns_master: the IP of DNS master
        :param description: A short description of the domain
        :param contact: contact email for the domain
        :return:
        """
        try:
            domain = Domain(name=name, dns_master=dns_master, description=description,
                            contact=contact)
            domain.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('domain', name, err)
        domain.save()
        return {
            'domain': domain.name,
            'status': 'done'
        }

    @staticmethod
    def update(name, dns_master=None, description=None, contact=None):
        """
        A custom way to update a domain.

        :param name: the name of the domain
        :param dns_master: the IP of DNS master
        :param description: A short description of the domain
        :param contact: contact email for the domain
        :return:
        """
        try:
            domain = Domain.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('domain', name, err)
        if dns_master is not None:
            domain.dns_master = dns_master
        if description is not None:
            domain.description = description
        if contact is not None:
            domain.contact = contact
        try:
            domain.full_clean()
        except (ValidationError, IntegrityError) as err:
            error_message('domain', name, err)
        domain.save()
        return {
            'domain': name,
            'status': 'done'
        }

    @staticmethod
    def remove(name):
        """
        This method is a custom way to delete a domain. As models.Model already have a method
        called delete(), we must use another name for our method.

        :param name: domain name
        :return:
        """
        try:
            domain = Domain.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('domain', name, err)
        domain.delete()
        return {
            'domain': name,
            'status': 'done'
        }

    @staticmethod
    def get(name, short=False):
        """
        A custom way to get a domain.
        :param name: the name of the domain
        :return:
        """
        try:
            domain = Domain.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('domain', name, err)
        result = domain.show(short=short)
        return result

    @staticmethod
    def search(filters=None):
        """
        This is a custom way to get all domains that match the filters
        :param filters: a dict of field / regex
        :return:
        """
        if filters is None:
            domains = Domain.objects.all()
        else:  # We suppose filters as been construct outside models class.
            domains = Domain.objects.filter(**filters)
        result = []
        for domain in domains:
            result.append(domain.show(short=True))
        return result


class DomainEntry(models.Model):
    """
    Domain entry is a name in domain like www.example.com
    - name: the name of the entry
    - domain: the domain associated (fqdn is name.domain)
    - type: the DNS entry type (A, CNAME, NS, ...). AAAA entries are marked as A type
    - entries: In some cases (CNAME, NS, ...) entry refered to another entry
    - description: a short description of the entry
    - creation_date: when entry as been created
    """
    name = models.CharField(max_length=50)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    type = models.CharField(max_length=5, default='A')
    entries = models.ManyToManyField('self')
    description = models.CharField(max_length=150, blank=True, default='', null=True)
    creation_date = models.DateField(auto_now_add=True, null=True)

    class Meta:
        """
        DomainEntry is unique for a specific domain (ie we only have one www.example.com but
        we can have www.example.org)
        """
        unique_together = ('name', 'domain', 'type')

    def show(self, key=False, short=False):
        """

        :param key:
        :param short:
        :return:
        """
        if key:
            result_addresses = []
            for address in self.address_set.all():
                result_addresses.append(address.show(key=True))
            result = {
                'name': self.name,
                'domain': self.domain.show(key=True),
                'type': self.type,
                'addresses': result_addresses
            }
        elif short:
            result_entries = []
            result_addresses = []
            for sub_entry in self.entries.all():
                result_entries.append(sub_entry.show(key=True))
            for address in self.address_set.all():
                result_addresses.append(address.show(key=True))
            result = {
                'name': self.name,
                'domain': self.domain.show(key=True),
                'type': self.type,
                'description': self.description,
                'creation_date': self.creation_date,
                'entries': result_entries,
                'addresses': result_addresses
            }
        else:
            result_entries = []
            result_addresses = []
            for sub_entry in self.entries.all():
                result_entries.append(sub_entry.show(short=True))
            for address in self.addresses_set.all():
                result_addresses.append(address.show(key=True))
            result = {
                'name': self.name,
                'domain': self.domain.show(short=True),
                'type': self.type,
                'description': self.description,
                'creation_date': self.creation_date,
                'entries': result_entries,
                'addresses': result_addresses
            }
        return result

    @staticmethod
    def create(name, domain, ns_type='A', sub_entry=None, description=None):
        """
        This method is a custom way to create NS entry.

        :param name: the name of the entry
        :param domain: the domain
        :param ns_type: the NS type of the entry
        :param sub_entry:
        :param description: A short description of the entry
        :return:
        """
        try:
            entry_domain = Domain.objects.get(name=domain)
        except ObjectDoesNotExist as err:
            return error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        try:
            entry = DomainEntry(name=name, domain=entry_domain, type=ns_type,
                                description=description)
            entry.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        entry.save()
        if sub_entry is not None:
            sub_entry_domain = Domain.objects.get(name=sub_entry['domain'])
            sub_entry_obj = DomainEntry.objects.get(name=sub_entry['name'],
                                                    domain=sub_entry_domain,
                                                    type=sub_entry['type'])
            entry.entries.add(sub_entry_obj)
        return {
            'entry': '{}.{} {}'.format(name, domain, ns_type),
            'status': 'done'
        }

    @staticmethod
    def update(name, domain, ns_type='A', sub_entry=None, description=None):
        """

        :param name:
        :param domain:
        :param ns_type:
        :param sub_entry:
        :param description:
        :return:
        """
        try:
            entry = DomainEntry(name=name, domain=domain, type=ns_type)
        except ObjectDoesNotExist as err:
            error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        if description is not None:
            entry.description = description
        if sub_entry is not None:
            sub_entry_obj = DomainEntry(name=sub_entry['name'], domain=sub_entry['domain'],
                                        type=sub_entry['type'])
            entry.entries.add(sub_entry)
        return {
            'entry': '{}.{} {}'.format(name, domain, ns_type),
            'status': 'done'
        }

    @staticmethod
    def exclude(name, domain, ns_type='A', sub_entry=None):
        """

        :param name:
        :param domain:
        :param ns_type:
        :param sub_entry:
        :return:
        """
        try:
            entry = DomainEntry(name=name, domain=domain, type=ns_type)
        except ObjectDoesNotExist as err:
            error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        if sub_entry is not None:
            sub_entry_obj = DomainEntry(name=sub_entry['name'], domain=sub_entry['domain'],
                                        type=sub_entry['type'])
            entry.entries.remove(sub_entry)
        return {
            'entry': '{}.{} {}'.format(name, domain, ns_type),
            'status': 'done'
        }

    @staticmethod
    def remove(name, domain, ns_type='A'):
        """
        A custom way to delete a entry. As a entry is unique from name/domain/ns_type, we need
        to have all this information to delete the right entry.

        :param name: name of entry
        :param domain: domain of entry
        :param ns_type: NS type of entry
        :return:
        """
        try:
            entry_domain = Domain.objects.get(name=domain)
            entry = DomainEntry.objects.get(name=name, domain=entry_domain, type=ns_type)
        except ObjectDoesNotExist as err:
            return error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        entry.delete()
        return {
            'entry': '{}.{} {}'.format(name, domain, ns_type),
            'status': 'done'
        }

    @staticmethod
    def get(name, domain, ns_type='A'):
        """
        A custom way to get a entry
        :param name: name of the entry
        :param domain: domain of the entry
        :param ns_type: NS type of the entry
        :return:
        """
        try:
            domain_entry = Domain.objects.get(name=domain)
        except ObjectDoesNotExist as err:
            return error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        try:
            entry = DomainEntry.objects.get(name=name, domain=domain_entry, type=ns_type)
        except ObjectDoesNotExist as err:
            return error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        return entry.show()

    @staticmethod
    def search(filters=None):
        """
        This is a custom method to get all entries
        :param filters: the filter we will use
        :return:
        """
        result = []
        if filters is None:
            entries = DomainEntry.objects.all()
        else:
            entries = DomainEntry.objects.filter(**filters)
        for entry in entries:
            result.append(entry.show(short=True))
        return result
