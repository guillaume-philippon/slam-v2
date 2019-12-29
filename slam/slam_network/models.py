from django.db import models


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
