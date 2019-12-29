"""
This module provide different view to manage domain. To avoid shadow name declaration, we use those
following nomenclature
 - network: a specific network (per example 192.168.0.0/24)
 - networks: a list of networks
 - host: a host is a association between a network (or a IP) with a DNS entry
 - *_view: a function that manage the web interface (per example domains_view manage web interface
 of domains, ...)
 - rest_api: a boolean which say if REST API is used. If not, HTML rendering will be used
 - options: a generic structure that represent arguments we send/receive to/from function
 - result: a temporary structure that represent the output of the view
 - result_*: a temporary structure that represent a part of the output (per example result_entries)
 - uri_*: input retrieve from URI structure itself
"""
from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required

from slam_network.models import Network


@login_required
def networks_view(request):
    """
    This function manage interaction between user and SLAM for all network management. URI is
    represented by https://slam.example.com/networks

    :param request: full HTTP request from user
    """
    result = []
    rest_api = False
    networks = Network.objects.all()
    for network in networks:
        result.append({
            'name': network.name,
            'description': network.description,
            'address': network.address,
            'prefix': network.prefix,
            'gateway': network.gateway,
            'dns-master': network.dns_master,
            'vlan': network.vlan,
            'dhcp': network.dhcp
        })
    return JsonResponse(result, safe=False)


@login_required
def network_view(request, uri_network):
    """
    This function manage interaction between user and SLAM for network management. URI is
    represented by https://slam.example.com/networks/my-network

    :param request: full HTTP request from user
    :param uri_network: the network name
    """
    rest_api = False
    result = {}
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        rest_api = True
    if request.method == 'GET':
        # If we want to get (GET) information about a network, we're looking for it and send
        # information
        network = Network.objects.get(name=uri_network)
        result = {
            'name': uri_network,
            'description': network.description,
            'contact': network.contact,
            'address': network.address,
            'prefix': network.prefix,
            'gateway': network.gateway,
            'dns-master': network.dns_master,
            'vlan': network.vlan,
            'dhcp': network.dhcp
        }
    elif request.method == 'POST':
        # If we want to create (POST) a new network, we retrieve information from POST and
        # see if optional value are put into it. If not, we ignore them.
        description = request.POST.get('description')
        address = request.POST.get('address')
        prefix = request.POST.get('prefix')
        gateway = request.POST.get('gateway')
        dns_master = request.POST.get('dns-master')
        contact = request.POST.get('contact')
        dhcp = request.POST.get('dhcp')
        vlan = request.POST.get('vlan')
        options = {
            'name': uri_network,
            'address': address,
            'prefix': prefix,
        }
        if description is not None:
            options['description'] = description
        if contact is not None:
            options['contact'] = contact
        if gateway is not None:
            options['dns_master'] = dns_master
        if dhcp is not None:
            options['dhcp'] = dhcp
        if vlan is not None:
            options['vlan'] = vlan
        Network.objects.create(**options)
        result = {
            'network': uri_network,
            'status': 'done'
        }
    elif request.method == 'PUT':
        # If we want to update (PUT) information, we need to retrieve data from body (no
        # request.PUT.get is available on django), and see which value should be updated.
        raw_data = request.body
        data = QueryDict(raw_data)
        description = data.get('description')
        contact = data.get('contact')
        gateway = data.get('gateway')
        dns_master = data.get('dns-master')
        dhcp = data.get('dhcp')
        vlan = data.get('vlan')
        network = Network.objects.get(name=uri_network)
        if description is not None:
            network.description = description
        if contact is not None:
            network.contact = contact
        if gateway is not None:
            network.gateway = gateway
        if dns_master is not None:
            network.dns_master = dns_master
        if dhcp is not None:
            network.dhcp = dhcp
        if vlan is not None:
            network.vlan = vlan
        network.save()
        result = {
            'network': uri_network,
            'status': 'done'
        }
    elif request.method == 'DELETE':
        # If we want to delete (DELETE) a network, we must find it and call delete method
        network = Network.objects.get(name=uri_network)
        network.delete()
        result = {
            'network': uri_network,
            'status': 'done'
        }
    else:
        # We just support GET / POST / PUT / DELETE HTTP method, in other case, we send a error
        result = {
            'network': uri_network,
            'status': 'failed',
            'reason': '{} method is not supported'.format(request.method)
        }
    return JsonResponse(result, safe=False)


@login_required
def host_view(request, uri_network, uri_host):
    """
    This function manage interaction between user and SLAM for a specific host. URI is represented
    by https://slam.example.com/networks/my-network

    :param request: full HTTP request from user
    :param uri_network: the name of the network from URI
    :param uri_host: the name of the host from URI
    """
    rest_api = False
    result = {}
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        rest_api = True
    if request.method == 'POST':
        network = Network.objects.get(name=uri_network)
        options = {
            'name': uri_host,
        }
    return JsonResponse(result)
