from django.db import models

from slam_hardware.models import Interface
from slam_network.models import Network
from slam_domain.models import DomainEntry


class Host(models.Model):
    name = models.CharField(max_length=150, unique=True)
    ip_address = models.GenericIPAddressField(unique=True, null=True, blank=True)
    interface = models.ForeignKey(Interface, on_delete=models.DO_NOTHING, null=True, blank=True)
    network = models.ForeignKey(Network, on_delete=models.DO_NOTHING, null=True, blank=True)
    dns_entry = models.ForeignKey(DomainEntry, on_delete=models.DO_NOTHING, null=True, blank=True)
