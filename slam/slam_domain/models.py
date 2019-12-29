"""
This module provide model for domains. There are 2 models
 - Domain: which represent a DNS domain like example.com
 - DomainEntry: which represent a named entry like www.example.com

As we use meta class from django that not require any public method, we disable pylint
for R0903 (too-few-public-methods)
"""
# pylint: disable=R0903
from django.db import models
from django.utils import timezone


class Domain(models.Model):
    """
    Domain class represent a fqdn domain like example.com
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=120, blank=True)
    dns_master = models.GenericIPAddressField()
    contact = models.EmailField(blank=True)


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
        unique_together = (('name', 'domain'))
