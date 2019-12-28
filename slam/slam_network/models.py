from django.db import models
from django.utils import timezone

from slam_domain.models import DomainEntry


class Network(models.Model):
    """
    Network class represent a IPv4 or IPv6 network
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=150, default='')
    address = models.GenericIPAddressField(unique=True)
    prefix = models.IntegerField(default=24)
    gateway = models.GenericIPAddressField(blank=True, null=True)
    dns_master = models.GenericIPAddressField(blank=True, null=True)
    contact = models.EmailField(blank=True, null=True)
    dhcp = models.GenericIPAddressField(blank=True, null=True)
    vlan = models.IntegerField(default=1)


# class Host(models.Model):
#     """
#     Host class represent link between DNS entry and IP
#     """
#     main_ns_entry = models.ForeignKey(DomainEntry, on_delete=models.DO_NOTHING)
#     address = models.GenericIPAddressField(blank=True, null=True)
#     network = models.ForeignKey(Network, on_delete=models.DO_NOTHING)
#     creation_date = models.DateField(default=timezone.now)
