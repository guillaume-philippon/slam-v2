"""
This module provide different view to manage hosts. To avoid shadow name declaration, we use those
following nomenclature
 - host: a host is a relation between a interface, a network and a domain entry
 - hosts: a list of host
 - interface: a physical interface represented by a MAC address
 - interfaces: a list of interface
 - network: a IPv4 or IPv6 network
 - ip_address: a IPv4 or IPv6 address
 - domain: a DNS domain
 - ns_entry: a DNS entry

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
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required
from slam_host.models import Host


@login_required
def hosts_view(request):
    # pylint: disable=W0613
    """
    This function manage interaction between user and SLAM for hosts management. URI is
    represented by https://slam.example.com/hosts
    :param request: full HTTP request from user
    :return:
    """
    result = Host.search()
    return JsonResponse(result, safe=False)


@login_required
def host_view(request, uri_host):
    """
    This function manage interaction between user and SLAM for host management. URI is
    represented by https://slam.example.com/hosts/host.example.com
    :param request: full HTTP request from user
    :param uri_host: host name from URI
    :return:
    """
    result = {
        'status': 'done'
    }
    if request.method == 'POST':
        options = {
            'name': uri_host,
        }
        if request.POST.get('interface') is not None:
            options['interface'] = request.POST.get('interface')
        if request.POST.get('network') is not None:
            options['network'] = request.POST.get('network')
        if request.POST.get('ns') is not None and \
                request.POST.get('domain') is not None:
            options['dns_entry'] = {
                'name': request.POST.get('ns'),
                'domain': request.POST.get('domain')
            }
        if request.POST.get('ip-address') is not None:
            options['address'] = request.POST.get('ip-address')
        result = Host.create(**options)
    elif request.method == 'DELETE':
        result = Host.remove(uri_host)
    elif request.method == 'GET':
        result = Host.get(uri_host)
    elif request.method == 'PUT':
        raw_data = request.body
        data = QueryDict(raw_data)
        options = dict()
        for args in data:
            # We don't care about the saintly of options as Host.update take care of it.
            options[args] = data.get(args)
        result = Host.update(uri_host, **options)
    else:
        # We just support GET / POST / PUT / DELETE HTTP method. If anything else arrived, we
        # just drop it.
        result = {
            'host': uri_host,
            'status': 'failed',
            'message': '{} method is not supported'.format(request.method)
        }
    return JsonResponse(result)
