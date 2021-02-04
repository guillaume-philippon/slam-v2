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
import logging
import json

from datetime import datetime
from distutils.util import strtobool

from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required

from slam_host.models import Host

LOGGER = logging.getLogger('api')


@login_required
def hosts_view(request):
    """
    This function manage interaction between user and SLAM for hosts management. URI is
    represented by https://slam.example.com/hosts

    We currently support only GET method.

    :param request: full HTTP request from user
    :return:
    """
    if request.method == 'GET' and request.headers['Accept'] != 'application/json':
        return render(request, 'host/hosts.html', dict())
    result = Host.search()
    return JsonResponse(result, safe=False)


@login_required
def host_view(request, uri_host):
    """
    This function manage interaction between user and SLAM for host management. URI is
    represented by https://slam.example.com/hosts/host.example.com. We supported the following
    method:
      - GET: to get a Host, in case of headers 'Accept' is not 'application/json', so we return a
        HTML render
      - POST: to create a Host
      - DELETE: to delete a Host
      - PUT: to modify a Host

    :param request: full HTTP request from user
    :param uri_host: host name from URI
    :return:
    """
    if request.method == 'GET' and request.headers['Accept'] != 'application/json':
        return render(request, 'host/host.html', dict())
    if request.method == 'POST':  # If we request to create a Host
        options = {
            'name': uri_host,
            'options': dict()
        }
        if request.POST.get('interface') is not None:  # If we create a Host w/ a interface
            options['interface'] = request.POST.get('interface')
        if request.POST.get('network') is not None:  # If we provide network name as param
            options['network'] = request.POST.get('network')
        if request.POST.get('owner') is not None:  # If we provide owner information
            options['owner'] = request.POST.get('owner')
        if request.POST.get('ns') is not None and \
                request.POST.get('domain') is not None:  # If we provide all info for NS record
            options['dns_entry'] = {
                'name': request.POST.get('ns'),
                'domain': request.POST.get('domain')
            }
        if request.POST.get('ip_address') is not None:  # If we provide a specific IP address
            options['address'] = request.POST.get('ip_address')
        if request.POST.get('no_ip') is not None:  # If we provide any info about auto assignement.
            options['options']['no_ip'] = strtobool(request.POST.get('no_ip'))
        else:
            options['options']['no_ip'] = False
        if request.POST.get('dhcp') is not None:  # If we provide any info about DHCP generation
            options['options']['dhcp'] = strtobool(request.POST.get('dhcp'))
        else:
            options['options']['dhcp'] = True

        LOGGER.info('{}: {} created host {} with options {}'.format(
            datetime.now(),
            request.user,
            uri_host,
            json.dumps(options)))
        result = Host.create(**options)
    elif request.method == 'DELETE':  # If we request to delete a Host
        LOGGER.info('{}: {} deleted host {}'.format(
            datetime.now(),
            request.user,
            uri_host))
        result = Host.remove(uri_host)
    elif request.method == 'GET':  # If we request to get a dict abstraction of a Host
        result = Host.get(uri_host)
    elif request.method == 'PUT':  # If we request to update a Host
        # As PUT is not a legacy HTTP request (only GET and POST were available first), we need
        # a special way to get data
        raw_data = request.body  # Get request.body will return something like foo=value&bar=value2
        # string
        data = QueryDict(raw_data)  # We create a QueryDict to have it easiest to manipulate
        options = dict()
        for args in data:
            # We don't care about the sanity of options as Host.update take care of it.
            options[args] = data.get(args)
        LOGGER.info('{}: {} updated host {} with options {}'.format(
            datetime.now(),
            request.user,
            uri_host,
            json.dumps(options)))
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


@login_required
def address_view(request, uri_host, uri_address):
    """
    This function manage interaction between user and SLAM to manage IP address list of a Host. URI
    is represented by https://slam.example.com/hosts/host.example.com/192.168.0.1

    We currently support only POST method.

    :param request: full HTTP request from user
    :param uri_host: the host name
    :param uri_address: the IP address
    :return:
    """
    result = {
        'address': uri_address,
        'status': 'failed',
        'message': 'This is a test'
    }
    if request.method == 'POST':
        options = dict()
        for arg in request.POST:
            options[arg] = request.POST.get(arg)
        result = Host.add(uri_host, uri_address, args=options)
    return JsonResponse(result)
