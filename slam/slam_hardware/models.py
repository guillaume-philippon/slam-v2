from django.db import models
from django.utils import timezone
from django.core.validators import ValidationError
import re


def mac_address_validator(mac_address):
    """
    This function check if a mac-address have a good format (ie 00:11:22:33:44:55)

    :param mac_address: mac-address provided by user
    :return:
    """
    regex = r'([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])'
    pattern = re.compile(regex)
    if not pattern.match(mac_address):
        raise ValidationError('Invalid MAC address format')


class Hardware(models.Model):
    """
    A hardware represent a physical machine. A hardware can have devices like interface.
    """
    name = models.CharField(max_length=50, unique=True)
    buying_date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=150)
    owner = models.CharField(max_length=150)
    vendor = models.CharField(max_length=150, default='')
    model = models.CharField(max_length=150, default='')
    serial_number = models.CharField(max_length=150, default='')
    inventory = models.CharField(max_length=150, default='')
    warranty = models.IntegerField(default=5)


class Interface(models.Model):
    """
    A interface represent a specific hardware device. A physical machine can have more than one
    interface device but a device is only attached to one and only one hardware.
    """
    INTERFACE_TYPE = (
        ('copper', 'Copper interface'),
        ('fiber', 'Fiber interface'),
        ('wireless', 'Wireless interface')
    )
    mac_address = models.CharField(max_length=17, unique=True,
                                   validators=[mac_address_validator])
    type = models.CharField(max_length=8, choices=INTERFACE_TYPE, null=True, blank=True)
    speed = models.IntegerField(null=True, blank=True)
    hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE, null=True, blank=True)
