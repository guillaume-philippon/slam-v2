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

 As django models are generic classes, pylint can't check if member of model Class exists, we must
 disable pylint E1101 (no-member) test from this file
"""
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required

from slam_hardware.models import Hardware, Interface


@login_required
def inventory_view(request):
    # pylint: disable=W0613
    """
    This function manage interaction between user and SLAM for hardware management. URI is
    represented by https://slam.example.com/hardware

    As we use django view that need request as argument but we not use it, we disable pylint.
    :param request: full HTTP request from user
    """
    result = Hardware.search()
    return JsonResponse(result, safe=False)


@login_required
def interface_view(request, uri_hardware, uri_interface):
    """
    This function manage interaction between user and SLAM interface for ethernet interface
    management. URI is represented by
    https://slam.example.com/hardware/my-computer/interfaces/00:11:22:33:44:55

    :param request: full HTTP request from user
    :param uri_hardware: the hardware where interface is attached
    :param uri_interface: the ethernet interface
    :return:
    """
    result = dict()
    if request.method == 'POST':
        options = {
            'mac_address': uri_interface,
            'hardware': uri_hardware
        }
        if request.POST.get('interface_type') is not None:
            options['type'] = request.POST.get('interface_type')
        if request.POST.get('interface_speed') is not None:
            options['speed'] = request.POST.get('interface_speed')
        result = Interface.create(**options)
    elif request.method == 'DELETE':
        result = Interface.remove(uri_interface)
    return JsonResponse(result)


@login_required
def hardware_view(request, uri_hardware):
    # pylint: disable=R0912
    """
    This view manage interaction with hardware. A hardware is a representation of a real machine.
    URI is represented by https://slam.example.com/hardware/my-machine

    :param request: full HTTP request from user
    :param uri_hardware: the name of the hardware from URI
    """
    if request.method == 'POST':
        options = {
            'name': uri_hardware
        }
        # We start w/ hardware
        if request.POST.get('description') is not None:
            options['description'] = request.POST.get('description')
        if request.POST.get('owner') is not None:
            options['owner'] = request.POST.get('owner')
        if request.POST.get('vendor') is not None:
            options['vendor'] = request.POST.get('vendor')
        if request.POST.get('model') is not None:
            options['model'] = request.POST.get('model')
        if request.POST.get('serial_number') is not None:
            options['serial_number'] = request.POST.get('serial_number')
        if request.POST.get('inventory') is not None:
            options['inventory'] = request.POST.get('inventory')
        if request.POST.get('warranty') is not None:
            options['warranty'] = request.POST.get('warranty')
        # Now we look at interface options
        options_interface = {
            'mac_address': request.POST.get('interface_mac_address')
        }
        if request.POST.get('interface_speed'):
            options_interface['speed'] = request.POST.get('interface_speed')
        if request.POST.get('interface-type'):
            options_interface['type'] = request.POST.get('interface-type')
        options['interfaces'] = [
            options_interface
        ]
        result = Hardware.create(**options)
    elif request.method == 'GET':
        result = Hardware.get(uri_hardware)
    elif request.method == 'PUT':
        raw_data = request.body
        data = QueryDict(raw_data)
        options = {
            'name': uri_hardware
        }
        if data.get('buying_date') is not None:
            options['buying_date'] = data.get('buying_date')
        if data.get('description') is not None:
            options['description'] = data.get('description')
        if data.get('owner') is not None:
            options['owner'] = data.get('owner')
        if data.get('vendor') is not None:
            options['vendor'] = data.get('vendor')
        if data.get('model') is not None:
            options['model'] = data.get('model')
        if data.get('serial_number') is not None:
            options['serial_number'] = data.get('serial_number')
        if data.get('inventory') is not None:
            options['inventory'] = data.get('inventory')
        if data.get('warranty') is not None:
            options['warranty'] = data.get('warranty')
        result = Hardware.update(**options)
    elif request.method == 'DELETE':
        result = Hardware.remove(uri_hardware)
    return JsonResponse(result)
