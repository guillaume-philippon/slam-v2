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
    This function manage interaction between user and SLAM for hardware management. URI is represented
    by https://slam.example.com/hardware

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
def interfaces_view(request):
    return JsonResponse({})


@login_required
def hardware_view(request, uri_hardware):
    """
    This view manage interaction with hardware. A hardware is a representation of a real machine.
    URI is represented by https://slam.example.com/hardware/my-machine

    :param request: full HTTP request from user
    :param uri_hardware: the name of the hardware from URI
    """
    rest_api = False
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        rest_api = True
    if request.method == 'POST':
        description = request.POST.get('description')
        owner = request.POST.get('owner')
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
        Interface.objects.create(**options_interface)
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
            'interfaces': result_interfaces
        }
    elif request.method == 'PUT':
        raw_data = request.body
        data = QueryDict(raw_data)
        description = data.get('description')
        owner = data.get('owner')

    return JsonResponse(result)
