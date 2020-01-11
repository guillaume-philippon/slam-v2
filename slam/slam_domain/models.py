"""
This module provide model for domains. There are 2 models
  - Domain: which represent a DNS domain like example.com
  - DomainEntry: which represent a named entry like www.example.com
"""
# As we use meta class from django that not require any public method, we disable pylint
# for R0903 (too-few-public-methods)
# As we use django models.Model, pylint fail to find objects method. We must disable pylint
# test E1101 (no-member)
# pylint: disable=E1101,R0903
from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError

from slam_core.utils import error_message, name_validator

DOMAIN_FIELD = [
    'description',
    'dns_master',
    'contact'
]


class Domain(models.Model):
    """
    Domain class represent a fqdn domain like example.com
      - name: immutable name of the domain (example.com)
      - description: a short description of the domain
      - dns_master: IP of DNS master (used to push data in production)
      - contact: a contact email for the domain
      - creation_date: when domain has been created
    """
    name = models.CharField(max_length=50, unique=True, validators=[name_validator])
    description = models.CharField(max_length=120, blank=True, null=True)
    dns_master = models.GenericIPAddressField()
    contact = models.EmailField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)

    def show(self, key=False, short=False):
        """
        This method return a dict construction of the object. We have 3 types of output,
          - standard: all information about object it-self, short information about associated objects
            (like ForeignKey and ManyToManyField)
          - short: some basic information about object it-self, primary key of associated objects
          - key: primary key of the object

        :param short: if set to True, method return a short output
        :param key: if set to True, method return a key output. It will overwrite short param
        :return:
        """
        if key:
            result = {
                'name': self.name
            }
        elif short:
            result = {
                'name': self.name,
                'description': self.description,
                'entries_count': DomainEntry.objects.filter(domain=self).exclude(type='PTR').count()
            }
        else:
            result_entries = []
            entries = DomainEntry.objects.filter(domain=self).exclude(type='PTR')
            for entry in entries:
                result_entries.append(entry.show(key=True))
            result = {
                'name': self.name,
                'description': self.description,
                'dns_master': self.dns_master,
                'contact': self.contact,
                'creation_date': self.creation_date,
                'entries': result_entries
            }
        return result

    @staticmethod
    def create(name, args=None):
        """
        A custom way to create a domain.

        :param name: the DNS name
        :param args: some optional information about a domain
        :return:
        """
        try:
            domain = Domain(name=name)
            if args is not None:
                for arg in args:
                    if arg in DOMAIN_FIELD:
                        setattr(domain, arg, args[arg])
            domain.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('domain', name, err)
        domain.save()
        result = domain.show()
        result['status'] = 'done'
        return result

    @staticmethod
    def update(name, args=None):
        """
        A custom method to update a domain.

        :param name: the name of the domain
        :param args: field that must be updated
        :return:
        """
        try:  # First, we get the domain
            domain = Domain.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('domain', name, err)
        if args is not None:
            for arg in args:
                if arg in DOMAIN_FIELD:
                    setattr(domain, arg, args[arg])
        try:
            domain.full_clean()
        except (ValidationError, IntegrityError) as err:
            error_message('domain', name, err)
        domain.save()
        result = domain.show()
        result['status'] = 'done'
        return result

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
        :param short: Return a short version of the object
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
    name = models.CharField(max_length=50, validators=[name_validator])
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
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
        result_entries = []
        result_addresses = []
        if key:
            for sub_entry in self.entries.all():
                result_entries.append({
                    'name': '{}.{} ({})'.format(sub_entry.name, sub_entry.domain.name,
                                                sub_entry.type)
                })
            for address in self.address_set.all():
                result_addresses.append(address.show(key=True))
            result = {
                'name': self.name,
                'domain': self.domain.show(key=True),
                'type': self.type,
                'entries': result_entries,
                'addresses': result_addresses
            }
        elif short:
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
            for sub_entry in self.entries.all():
                result_entries.append(sub_entry.show(short=True))
            for address in self.address_set.all():
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
        sub_entry_obj = None
        if ' ' in name:
            return error_message('domain', name, 'Space not allowed in name')
        try:  # First, we get the domain
            entry_domain = Domain.objects.get(name=domain)
        except ObjectDoesNotExist as err:
            return error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        if sub_entry is not None:
            try:
                sub_entry_domain = Domain.objects.get(name=sub_entry['domain'])
                sub_entry_obj = DomainEntry.objects.get(name=sub_entry['name'],
                                                        domain=sub_entry_domain,
                                                        type=sub_entry['type'])
            except ObjectDoesNotExist as err:
                return error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        # We must check
        #  - if it s a A record, no similar CNAME
        #  - if it s a CNAME, no similar A record
        if ns_type == 'A':
            try:
                DomainEntry.objects.get(name=name, domain=entry_domain, type='CNAME')
                return error_message('entry', '{}.{} {}'.format(name, domain, ns_type),
                                     'A similar CNAME record exist !')
            except ObjectDoesNotExist:
                pass
        elif ns_type == 'CNAME':
            try:
                DomainEntry.objects.get(name=name, domain=entry_domain, type='A')
                return error_message('entry', '{}.{} {}'.format(name, domain, ns_type),
                                     'A similar A record exist !')
            except ObjectDoesNotExist:
                pass
        try:
            entry = DomainEntry(name=name, domain=entry_domain, type=ns_type,
                                description=description)
            entry.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('entry', '{}.{} {}'.format(name, domain, ns_type), err)
        entry.save()
        if sub_entry_obj is not None:
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
            if sub_entry['name']:
                return error_message('entry', '{}.{} {}'.format(name, domain, ns_type),
                                     'Space not allowed in name')
            sub_entry_obj = DomainEntry(name=sub_entry['name'], domain=sub_entry['domain'],
                                        type=sub_entry['type'])
            sub_entry_obj.full_clean()
            sub_entry_obj.save()
            entry.entries.add(sub_entry_obj)
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
            sub_entry_obj = DomainEntry.get(name=sub_entry['name'], domain=sub_entry['domain'],
                                        type=sub_entry['type'])
            entry.entries.remove(sub_entry_obj)
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
