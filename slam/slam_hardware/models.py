"""
This file provide model for SLAM hardware management.

As we use django models.Model, pylint fail to find objects method. We must disable pylint
test E1101 (no-member)
"""
# pylint: disable=E1101
import re

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError

from slam_core.utils import error_message


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
    description = models.CharField(max_length=150, default='', blank=True)
    owner = models.CharField(max_length=150, default='', blank=True)
    vendor = models.CharField(max_length=150, default='', blank=True)
    model = models.CharField(max_length=150, default='', blank=True)
    serial_number = models.CharField(max_length=150, default='', blank=True)
    inventory = models.CharField(max_length=150, default='', blank=True)
    warranty = models.IntegerField(default=5)

    @staticmethod
    def create(name, description=None, owner=None, vendor=None, model=None, serial_number=None,
               inventory=None, warranty=None, interfaces=None):
        # pylint: disable=R0913
        """
        This is a custom method to create a hardware
        :param name: name of the hardware
        :param description: A short description of the hardware
        :param owner: Owner of the hardware
        :param vendor: Hardware vendor name
        :param model: Hardware model name
        :param serial_number: Hardware Serial Number
        :param inventory: Inventory number
        :param warranty: Warranty duration
        :param interfaces: interfaces in the hardware
        :return:
        """
        try:
            hardware = Hardware(name=name)
            if description is not None:
                hardware.description = description
            if owner is not None:
                hardware.owner = owner
            if vendor is not None:
                hardware.vendor = vendor
            if model is not None:
                hardware.model = model
            if serial_number is not None:
                hardware.serial_number = serial_number
            if inventory is not None:
                hardware.inventory = inventory
            if warranty is not None:
                hardware.warranty = warranty
            hardware.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('hardware', name, err)
        hardware.save()
        if interfaces is not None:
            for interface in interfaces:
                try:
                    interface['hardware'] = hardware
                    interface_hw = Interface(**interface)
                    interface_hw.full_clean()
                except (IntegrityError, ValidationError) as err:
                    return error_message('interface', interface['mac_address'], err)
                interface_hw.save()
        return {
            'hardware': hardware.name,
            'status': 'done'
        }

    @staticmethod
    def update(name, buying_date=None, description=None, owner=None, vendor=None, model=None,
               serial_number=None, inventory=None, warranty=None):
        # pylint: disable=R0913
        """
        This is a custom method to update hardware information
        :param name: name of the hardware
        :param buying_date: when hardware as been bought
        :param description: a short description of the hardware
        :param owner: the owner of the hardware
        :param vendor: the vendor name of the hardware
        :param model: the model name of the hardware
        :param serial_number: hardware serial number
        :param inventory: hardware inventory id
        :param warranty: warranty duration
        :return:
        """
        try:
            hardware = Hardware.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('hardware', name, err)
        if buying_date is not None:
            hardware.buying_date = buying_date
        if description is not None:
            hardware.description = description
        if owner is not None:
            hardware.owner = owner
        if vendor is not None:
            hardware.vendor = vendor
        if model is not None:
            hardware.model = model
        if serial_number is not None:
            hardware.serial_number = serial_number
        if inventory is not None:
            hardware.inventory = inventory
        if warranty is not None:
            hardware.warranty = warranty
        try:
            hardware.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('hardware', name, err)
        hardware.save()
        return {
            'hardware': name,
            'status': 'done'
        }

    @staticmethod
    def remove(name):
        """
        This is a custom way to delete a hardware
        :return:
        """
        try:
            hardware = Hardware.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('hardware', name, err)
        try:
            hardware.delete()
        except IntegrityError as err:
            return error_message('hardware', name, err)
        return {
            'hardware': name,
            'status': 'done'
        }

    @staticmethod
    def get(name):
        """
        This is a custom method to get hardware information
        :param name: name of the hardware
        :return:
        """
        try:
            hardware = Hardware.objects.get(name=name)
            interfaces = Interface.objects.filter(hardware=hardware)
        except ObjectDoesNotExist as err:
            return error_message('hardware', name, err)
        result_interfaces = []
        for interface in interfaces:
            result_interfaces.append({
                'mac_address': interface.mac_address,
                'type': interface.type,
                'speed': interface.speed
            })
        return {
            'name': name,
            'buying_date': hardware.buying_date,
            'description': hardware.description,
            'owner': hardware.owner,
            'vendor': hardware.vendor,
            'model': hardware.model,
            'serial_number': hardware.serial_number,
            'inventory': hardware.inventory,
            'warranty': hardware.warranty,
            'interfaces': result_interfaces
        }

    @staticmethod
    def search(filters=None):
        """
        This is a custom way to get all hardware match the filter
        :param filters:
        :return:
        """
        if filters is None:
            inventory = Hardware.objects.all()
        else:
            inventory = Hardware.objects.filter(**filters)
        result = []
        for hardware in inventory:
            result.append({
                'name': hardware.name,
                'buying_date': hardware.name,
                'description': hardware.description,
                'owner': hardware.owner,
                'vendor': hardware.owner,
                'model': hardware.owner,
                'serial_number': hardware.owner,
                'inventory': hardware.owner,
                'warranty': hardware.owner,
            })
        return result


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
    type = models.CharField(max_length=8, choices=INTERFACE_TYPE, null=True, default='copper')
    speed = models.IntegerField(null=True, blank=True)
    hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE)

    @staticmethod
    def create(mac_address, hardware, int_type=None, speed=None):
        """
        This is a custom method to create a interface
        :param mac_address: mac address of the interface
        :param hardware: hardware where interface is attached
        :param int_type: interface type (copper, fiber, wireless)
        :param speed: interface speed
        :return:
        """
        try:
            hardware = Hardware.objects.get(name=hardware)
        except ObjectDoesNotExist as err:
            # If hardware not exist, we create it
            Hardware.create(name=hardware)
            hardware = Hardware.objects.get(name=hardware)
        options = {
            'mac_address': mac_address,
            'hardware': hardware,
        }
        if int_type is not None:
            options['type'] = int_type
        if speed is not None:
            options['speed'] = speed
        try:
            interface = Interface(**options)
            interface.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('interface', mac_address, err)
        interface.save()
        return {
            'interface': mac_address,
            'status': 'done'
        }

    @staticmethod
    def remove(mac_address):
        """
        This is a custom method to delete a interface
        :return:
        """
        try:
            interface = Interface.objects.get(mac_address=mac_address)
        except ObjectDoesNotExist as err:
            return error_message('interface', mac_address, err)
        interface.delete()
        return {
            'interface': mac_address,
            'status': 'done'
        }

    @staticmethod
    def get(mac_address):
        try:
            interface = Interface.objects.get(mac_address=mac_address)
        except ObjectDoesNotExist as err:
            return error_message('interface', mac_address, err)
        return {
            'mac_address': interface.mac_address,
            'type': interface.type,
            'speed': interface.speed,
            'hardware': interface.hardware.name
        }

    @staticmethod
    def search(filters=None):
        """
        This is a custom way to get all hardware match the filter
        :param filters:
        :return:
        """
        if filters is None:
            interface = Interface.objects.all()
        else:
            interface = Interface.objects.filter(**filters)
        result = []
        for interface in interface:
            result.append({
                'mac_address': interface.mac_address,
                'buying_date': interface.type,
                'description': interface.speed,
                'hardware': interface.hardware.name,
            })
        return result
