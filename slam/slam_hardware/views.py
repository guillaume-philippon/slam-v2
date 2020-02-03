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
    # As we use django view that need request as argument but we not use it, we disable pylint.
    # pylint: disable=W0613
    """
    This function manage interaction between user and SLAM for hardware management. URI is
    represented by https://slam.example.com/hardware

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
        options = dict()
        if request.POST.get('interface_type') is not None:
            options['type'] = request.POST.get('interface_type')
        if request.POST.get('interface_speed') is not None:
            options['speed'] = request.POST.get('interface_speed')
        result = Interface.create(mac_address=uri_interface, hardware=uri_hardware, args=options)
    elif request.method == 'DELETE':
        result = Interface.remove(uri_interface)
    elif request.method == 'GET':
        result = Interface.get(uri_interface)
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
    if request.method == 'POST':  # If we have a POST request (ie Hardware creation)
        options = dict()
        for arg in request.POST:  # For almost all things, that's right. We don't need to take care
            # of sanity of options as create do it.
            options[arg] = request.POST.get(arg)
        # But for interface it a little bit tricky as request.POST not authorized dict of dict.
        # All interface based request have a prefix interface. We build a specific options for it.
        options_interface = {
            'mac_address': request.POST.get('interface_mac_address')
        }
        if request.POST.get('interface_speed'):
            options_interface['speed'] = request.POST.get('interface_speed')
        if request.POST.get('interface-type'):
            options_interface['type'] = request.POST.get('interface-type')
        result = Hardware.create(name=uri_hardware, interfaces=[options_interface], args=options)
    elif request.method == 'GET':
        result = Hardware.get(uri_hardware)
    elif request.method == 'PUT':
        # As PUT is not a legacy method for HTTP the way to retrieve data is a little bit more
        # tricky
        raw_data = request.body
        data = QueryDict(raw_data)
        print(data)
        options = dict()
        for arg in data:  # We don't care about sanity, update method from Hardware do it.
            options[arg] = data.get(arg)
        print(uri_hardware)
        result = Hardware.update(name=uri_hardware, args=options)
    elif request.method == 'DELETE':
        result = Hardware.remove(uri_hardware)
    return JsonResponse(result)
