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
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required

from slam_network.models import Network, Address


@login_required
def networks_view(request):
    # pylint: disable=W0613
    """
    This function manage interaction between user and SLAM for all network management. URI is
    represented by https://slam.example.com/networks

    :param request: full HTTP request from user
    """
    result = Network.search()
    return JsonResponse(result, safe=False)


@login_required
def network_view(request, uri_network):
    """
    This function manage interaction between user and SLAM for network management. URI is
    represented by https://slam.example.com/networks/my-network

    :param request: full HTTP request from user
    :param uri_network: the network name
    """
    if request.method == 'GET':
        # If we want to get (GET) information about a network, we're looking for it and send
        # information
        result = Network.get(name=uri_network)
    elif request.method == 'POST':
        # If we want to create (POST) a new network, we retrieve information from POST and
        # see if optional value are put into it. If not, we ignore them.
        options = {
            'name': uri_network,
        }
        for arg in request.POST:
            # We don't care about saintly of options as Network.create take care of it.
            options[arg] = request.POST.get(arg)
        try:
            result = Network.create(**options)
        except TypeError as err:
            result = {
                'network': uri_network,
                'status': 'failed',
                'message': '{}'.format(err)
            }
    elif request.method == 'PUT':
        # If we want to update (PUT) information, we need to retrieve data from body (no
        # request.PUT.get is available on django), and see which value should be updated.
        raw_data = request.body
        data = QueryDict(raw_data)
        options = {
            'name': uri_network,
        }
        for arg in data:
            # We don't care about saintly of options as Network.update take care of it.
            options[arg] = data.get(arg)
        try:
            result = Network.update(**options)
        except TypeError as err:
            result = {
                'network': uri_network,
                'status': 'failed',
                'message': '{}'.format(err)
            }
    elif request.method == 'DELETE':
        # If we want to delete (DELETE) a network, we must find it and call delete method
        result = Network.remove(name=uri_network)
    else:
        # We just support GET / POST / PUT / DELETE HTTP method, in other case, we send a error
        result = {
            'network': uri_network,
            'status': 'failed',
            'reason': '{} method is not supported'.format(request.method)
        }
    return JsonResponse(result, safe=False)


@login_required
def address_view(request, uri_network, uri_address):
    """
    This function manage interaction between user and SLAM for a specific host. URI is represented
    by https://slam.example.com/networks/192.168.0.1

    :param request: full HTTP request from user
    :param uri_network: the name of the network from URI
    :param uri_address: the IP address from URI
    """
    result = {
        'address': uri_address,
        'status': 'failed',
        'message': 'This is a test'
    }
    if request.method == 'POST':
        options = {
            'ip': uri_address,
            'network': uri_network
        }
        options_entry = dict()
        if request.POST.get('name') is not None:
            options_entry['name'] = request.POST.get('name')
            options_entry['domain'] = request.POST.get('domain')
            options['ns_entry'] = options_entry
        result = Address.create(**options)
    elif request.method == 'DELETE':
        result = Address.remove(uri_address, uri_network)
    elif request.method == 'GET':
        result = Address.get(uri_address, uri_network)
    return JsonResponse(result)


@login_required
def entry_view(request, uri_network, uri_address, uri_entry):
    """
    This function manage interaction between user and SLAM for specific address. URI is represented
    by https://slam.example.com/networks/192.168.0.1/www.example.com
    :param request: full HTTP request from user
    :param uri_network: the name of the network from URI
    :param uri_address: the IP address from URI
    :param uri_entry: the NS entry from URI
    :return:
    """
    result = {
        'entry': uri_entry,
        'status': 'failed',
        'message': 'This is a test'
    }
    if request.method == 'POST':
        if request.POST.get('ns_type') is not None:
            result = Address.include(uri_address, uri_network, uri_entry,
                                     request.POST.get('ns_type'))
        else:
            result = Address.include(uri_address, uri_network, uri_entry)
    elif request.method == 'DELETE':
        raw_data = request.body
        data = QueryDict(raw_data)
        if data.get('ns_type') is not None:
            result = Address.exclude(uri_address, uri_network, uri_entry,
                                     data.get('ns_type'))
        else:
            result = Address.exclude(uri_address, uri_network, uri_entry)
    return JsonResponse(result)
