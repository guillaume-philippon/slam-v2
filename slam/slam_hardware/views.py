"""
This module provide different view to manage domain. To avoid shadow name declaration, we use those
following nomenclature
 - hardware: a hardware is a representation of real machine
 - inventory: a list of hardware
 - interface: a physical interface represented by a MAC address
 - interfaces: a list of interface

 - *_view: a function that manage the web interface (per example domains_view manage web interface
 of domains, ...)
 - rest_api: a boolean which say if REST API is used. If not, HTML rendering will be used
 - options: a generic structure that represent arguments we send to function
 - data: a generic structure that represent arguments we received from a function
 - result: a temporary structure that represent the output of the view
 - result_*: a temporary structure that represent a part of the output (per example result_entries)
 - uri_*: input retrieve from URI structure itself
 - raw_*: a raw version of variable
"""
from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required

from slam_hardware.models import Hardware, Interface


@login_required
def inventory_view(request):
    """
    This function manage interaction between user and SLAM for hardware management. URI is
    represented by https://slam.example.com/hardware

    :param request: full HTTP request from user
    """
    result = []
    inventory = Hardware.objects.all()
    for hardware in inventory:
        result.append({
            'name': hardware.name,
            'description': hardware.description,
            'owner': hardware.owner
        })
    return JsonResponse(result, safe=False)


@login_required
def interface_view(request, uri_hardware, uri_interface):
    result = dict()
    if request.method == 'POST':
        hardware = Hardware.objects.get(name=uri_hardware)
        options = {
            'mac_address': uri_interface,
            'hardware': hardware
        }
        if request.POST.get('interface-type') is not None:
            options['type'] = request.POST.get('interface-type')
        if request.POST.get('interface-speed') is not None:
            options['speed'] = request.POST.get('interface-speed')
        interface = Interface(**options)
        interface.clean_fields()
        interface.save()
        result = {
            'hardware': uri_hardware,
            'mac-address': options['mac_address'],
            'status': 'done'
        }
    elif request.method == 'DELETE':
        interface = Interface.objects.get(mac_address=uri_interface)
        interface.delete()
        result = {'interface': uri_interface,
                  'status': 'done'}
    return JsonResponse(result)


@login_required
def hardware_view(request, uri_hardware):
    """
    This view manage interaction with hardware. A hardware is a representation of a real machine.
    URI is represented by https://slam.example.com/hardware/my-machine

    :param request: full HTTP request from user
    :param uri_hardware: the name of the hardware from URI
    """
    rest_api = False
    result = dict()
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        rest_api = True
    if request.method == 'POST':
        description = request.POST.get('description')
        owner = request.POST.get('owner')
        vendor = request.POST.get('vendor')
        model = request.POST.get('model')
        serial_number = request.POST.get('serial-number')
        inventory = request.POST.get('inventory')
        warranty = request.POST.get('warranty')
        interface_address = request.POST.get('interface-mac-address')
        interface_speed = request.POST.get('interface-speed')
        interface_type = request.POST.get('interface-type')
        options_interface = {
            'mac_address': interface_address
        }
        options = {
            'name': uri_hardware
        }
        if description is not None:
            options['description'] = description
        if owner is not None:
            options['owner'] = owner
        if vendor is not None:
            options['vendor'] = vendor
        if model is not None:
            options['model'] = model
        if serial_number is not None:
            options['serial-number'] = serial_number
        if inventory is not None:
            options['inventory'] = inventory
        if warranty is not None:
            options['warranty'] = warranty
        try:
            Hardware.objects.create(**options)
        except:
            pass
        hardware = Hardware.objects.get(name=uri_hardware)

        if interface_type is not None:
            options_interface['type'] = interface_type
        if interface_speed is not None:
            options_interface['speed'] = interface_speed
        options_interface['hardware'] = hardware
        interface = Interface(**options_interface)
        interface.clean_fields()
        interface.save()
        result = {
            'hardware': uri_hardware,
            'status': 'done'
        }
    elif request.method == 'GET':
        hardware = Hardware.objects.get(name=uri_hardware)
        interfaces = Interface.objects.filter(hardware=hardware)
        result_interfaces = []
        for interface in interfaces:
            result_interfaces.append({
                'mac-address': interface.mac_address,
                'type': interface.type,
                'speed': interface.speed
            })
        result = {
            'name': uri_hardware,
            'description': hardware.description,
            'owner': hardware.owner,
            'vendor': hardware.vendor,
            'model': hardware.model,
            'serial-number': hardware.serial_number,
            'inventory': hardware.inventory,
            'buying-date': hardware.buying_date,
            'warranty': hardware.warranty,
            'interfaces': result_interfaces
        }
    elif request.method == 'PUT':
        raw_data = request.body
        data = QueryDict(raw_data)
        print(data)
        description = data.get('description')
        owner = data.get('owner')
        vendor = data.get('vendor')
        model = data.get('model')
        serial_number = data.get('serial-number')
        inventory = data.get('inventory')
        warranty = data.get('warranty')
        hardware = Hardware.objects.get(name=uri_hardware)
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
        hardware.save()
        result = {
            'hardware': uri_hardware,
            'status': 'done'
        }
    elif request.method == 'DELETE':
        hardware = Hardware.objects.get(name=uri_hardware)
        hardware.delete()
        result = {
            'hardware': uri_hardware,
            'status': 'done'
        }
    return JsonResponse(result)
