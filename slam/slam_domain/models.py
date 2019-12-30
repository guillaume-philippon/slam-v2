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
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError


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
        except IntegrityError as err:  # In case the domain already exist
            return {
                'domain': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        except ValidationError as err:  # In case of some validation issue w/ fields
            return {
                'domain': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
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
            return {
                'domain': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        if dns_master is not None:
            domain.dns_master = dns_master
        if description is not None:
            domain.description = description
        if contact is not None:
            domain.contact = contact
        domain.full_clean()
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
            return {
                'domain': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        domain.delete()
        return {
            'domain': name,
            'status': 'done'
        }

    @staticmethod
    def get(name):
        """
        A custom way to get a domain.
        :param name: the name of the domain
        :return:
        """
        result = {
            'domain': name,
        }
        try:
            domain = Domain.objects.get(name=name)
            result['description'] = domain.description
            result['dns_master'] = domain.dns_master
            result['contact'] = domain.contact
        except ObjectDoesNotExist as err:
            return {
                'domain': name,
                'status': 'failed',
                'message': '{}'.format(err)
            }
        entries = DomainEntry.objects.filter(domain=domain)
        result['entries'] = []
        for entry in entries:
            result['entries'].append({
                'name': entry.name,
                'type': entry.type,
                'description': entry.description
            })
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
            result.append({
                'name': domain.name,
                'description': domain.description
            })
        return result


class DomainEntry(models.Model):
    """
    Domain entry is a name in domain like www.example.com
    """
    name = models.CharField(max_length=50)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    type = models.CharField(max_length=5, default='A')
    description = models.CharField(max_length=150, blank=True, default='', null=True)
    creation_date = models.DateField(default=timezone.now)

    class Meta:
        """
        DomainEntry is unique for a specific domain (ie we only have one www.example.com but
        we can have www.example.org)
        """
        unique_together = ('name', 'domain', 'type')

    @staticmethod
    def create(name, domain, ns_type='A', description=None):
        """
        This method is a custom way to create NS entry.

        :param name: the name of the entry
        :param domain: the domain
        :param ns_type: the NS type of the entry
        :param description: A short description of the entry
        :return:
        """
        try:
            entry_domain = Domain.objects.get(name=domain)
        except ObjectDoesNotExist as err:
            return {
                'entry': '{}.{} {}'.format(name, domain, ns_type),
                'status': 'failed',
                'message': '{}'.format(err)
            }
        try:
            entry = DomainEntry(name=name, domain=entry_domain, type=ns_type,
                                description=description)
            entry.full_clean()
        except IntegrityError as err:
            return {
                'entry': '{}.{} {}'.format(name, domain, ns_type),
                'status': 'failed',
                'message': '{}'.format(err)
            }
        except ValidationError as err:
            return {
                'entry': '{}.{} {}'.format(name, domain, ns_type),
                'status': 'failed',
                'message': '{}'.format(err)
            }
        entry.save()
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
            return {
                'entry': '{}.{} {}'.format(name, domain, ns_type),
                'status': 'failed',
                'message': '{}'.format(err)
            }
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
            return {
                'entry': '{}.{} {}'.format(name, domain, ns_type),
                'status': 'failed',
                'message': '{}'.format(err)
            }
        try:
            entry = DomainEntry.objects.get(name=name, domain=domain_entry, type=ns_type)
        except ObjectDoesNotExist as err:
            return {
                'entry': '{}.{} {}'.format(name, domain, ns_type),
                'status': 'failed',
                'message': '{}'.format(err)
            }
        return {
            'name': entry.name,
            'domain': entry.domain.name,
            'type': entry.type,
            'description': entry.description,
            'created': entry.creation_date
        }
