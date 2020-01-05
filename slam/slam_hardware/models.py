"""
This module provide Hardware and Interface models and all associated method.

For Hardware
  - Hardware.show: method to return a dict abstraction of a Hardware
  - Hardware.create: a staticmethod to create a Hardware w/ some check associated to it
  - Hardware.update: a staticmethod to update Hardware field
  - Hardware.remove: a staticmethod to delete a Hardware w/ some check associated to it
  - Hardware.add: a staticmethod to add a Interface to a Hardware
  - Hardware.get: a staticmethod to get a dict abstraction of a Hardware w/o instanciate it before
  - Hardware.search: a staticmethod to get all Hardware match the filter

For Interface
  - Interface.show: method to return a dict abstraction of a Interface
  - Interface.create: a staticmethod to create a Interface w/ some check associated to it
  - Interface.update: a staticmethod to update Interface field
  - Interface.remove: a staticmethod to delete a Interface w/ some check associated to it
  - Interface.add: a staticmethod to add a IP to a Interface
  - Interface.get: a staticmethod to get a dict abstraction of a Interface w/o instanciate it before
  - Interface.search: a staticmethod to get all Interface match the filter
"""
# As we use django models.Model, pylint fail to find objects method. We must disable pylint
# test E1101 (no-member)
# pylint: disable=E1101
import re

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError

from slam_core.utils import error_message

HARDWARE_FIELD = [
    'name',
    'buying_date',
    'description',
    'owner',
    'vendor',
    'model',
    'serial_number',
    'inventory',
    'warranty'
]

INTERFACE_FIELD = [
    'mac_address',
    'type',
    'speed'
]


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
    A Hardware represent a physical machine.
      - name: a hardware name, there are no relation between hardware name and NS record
        by default, it's build by Host.create named it name-mac_address
      - buying_date: when hardware has been buy. By default, it's when it's created
      - description: a short description of the machine
      - owner: the owner of the machine
      - vendor: manifacturor name of the machine
      - model: the model of the machine
      - serial_number: unique serial number from manifacturer
      - inventory: local inventory identifier
      - warranty: warranty duration
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

    def interfaces(self):
        """
        This method return all Interfaces attached to this hardware. A hardware can have more than
        one Interface.

        :return:
        """
        return self.interface_set.all()
        # return Interface.objects.filter(hardware=self)

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
            result_interfaces = []
            for interface in self.interfaces():
                result_interfaces.append(interface.show(key=True))
            result = {
                'name': self.name,
                'buying_date': self.buying_date,
                'description': self.description,
                'owner': self.owner,
                'interfaces': result_interfaces
            }
        else:
            result_interfaces = []
            for interface in self.interfaces():
                result_interfaces.append(interface.show(short=True))
            result = {
                'name': self.name,
                'buying_date': self.buying_date,
                'description': self.description,
                'owner': self.owner,
                'vendor': self.vendor,
                'model': self.model,
                'serial_number': self.serial_number,
                'inventory': self.inventory,
                'warranty': self.warranty,
                'interfaces': result_interfaces
            }
        return result

    @staticmethod
    def create(name, interfaces=None, args=None):
        """
        This is a custom method to create a hardware. args represent all Hardware self attributes.
        interfaces represent a list of interface.

        :param name: name of the hardware
        :param interfaces: interfaces in the hardware
        :param args: a dict of field used to create the hardware
        :return:
        """
        try:
            hardware = Hardware(name=name)
            if args is not None:
                for arg in args:
                    if arg in HARDWARE_FIELD:  # We just keep args which are useful for Hardware
                        # creation
                        setattr(hardware, arg, args[arg])
            hardware.full_clean()
        except (IntegrityError, ValidationError) as err:  # if something go wrong we stay here
            return error_message('hardware', name, err)
        hardware.save()
        if interfaces is not None:  # If we have some interfaces to add
            for interface in interfaces:
                try:
                    interface['hardware'] = hardware
                    interface_hw = Interface(**interface)
                    interface_hw.full_clean()
                except (IntegrityError, ValidationError) as err:
                    return error_message('interface', interface['mac_address'], err)
                interface_hw.save()
        result = hardware.show()
        result['status'] = 'done'
        return result

    @staticmethod
    def update(name, args=None):
        """
        This is a custom method to update hardware information. We just update Hardware self
        information. Adding, remove or update interface is not done by the same way.

        :param name: name of the hardware
        :param args: All information that must be updated
        :return:
        """
        try:  # First, we get the hardware
            hardware = Hardware.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('hardware', name, err)
        for arg in args:
            if arg in HARDWARE_FIELD:  # We just keep args that is useful for Hardware
                setattr(hardware, arg, args[arg])
        try:  # Just in case
            hardware.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('hardware', name, err)
        hardware.save()
        result = hardware.show()
        result['status'] = 'done'
        return result

    @staticmethod
    def remove(name):
        """
        This is a custom way to delete a hardware. As django model have its own delete method, we
        call it remove.

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
        This is a custom method to get hardware information.

        :param name: name of the hardware
        :return:
        """
        try:
            hardware = Hardware.objects.get(name=name)
        except ObjectDoesNotExist as err:
            return error_message('hardware', name, err)
        return hardware.show()

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
            result.append(hardware.show(short=True))
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
                'mac_address': self.mac_address
            }
        # elif short:
        #     result = {
        #         'mac_address': self.mac_address,
        #         'hardware': self.hardware.show(short=True)
        #     }
        else:
            result = {
                'mac_address': self.mac_address,
                'type': self.type,
                'speed': self.speed,
                'hardware': self.hardware.show(short=True)
            }
        return result

    @staticmethod
    def create(mac_address, hardware, args=None):
        """
        This is a custom method to create a interface
        :param mac_address: mac address of the interface
        :param hardware: hardware where interface is attached
        :param args: options for Interface creation
        :return:
        """
        try:  # First, we see if hardware exist
            hardware = Hardware.objects.get(name=hardware)
        except ObjectDoesNotExist:
            # If hardware not exist, we create it
            Hardware.create(name=hardware)
            hardware = Hardware.objects.get(name=hardware)
        try:
            interface = Interface(mac_address=mac_address)
            setattr(interface, 'hardware', hardware)
            if args is not None:
                for arg in args:
                    if arg in INTERFACE_FIELD:
                        setattr(interface, arg, args[arg])
            interface.full_clean()
        except (IntegrityError, ValidationError) as err:
            return error_message('interface', mac_address, err)
        interface.save()
        result = interface.show()
        result['status'] = 'done'
        return result

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
    def get(mac_address, short=False):
        try:
            interface = Interface.objects.get(mac_address=mac_address)
        except ObjectDoesNotExist as err:
            return error_message('interface', mac_address, err)
        return interface.show(short)

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
            result.append(interface.show(short=True))
        return result
