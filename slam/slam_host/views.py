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
from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from slam_hardware.models import Interface
from slam_network.models import Network
from slam_domain.models import DomainEntry, Domain
from slam_host.models import Host
from slam_host.networks import get_network_from, get_free_ip_from


@login_required
def hosts_view(request):
    """
    This function manage interaction between user and SLAM for hosts management. URI is
    represented by https://slam.example.com/hosts
    :param request: full HTTP request from user
    :return:
    """
    result = []
    hosts = Host.objects.all()
    for host in hosts:
        result.append({
            'name': host.name,
            'ip-address': host.ip_address
        })
    return JsonResponse(result, safe=False)


@login_required
def host_view(request, uri_host):
    """

    :param request:
    :param uri_host:
    :return:
    """
    result = {
        'status': 'done'
    }
    if request.method == 'POST':
        # interface = None
        # network = None
        # ns = None
        try:
            if request.POST.get('interface') is not None:
                interface = Interface.objects.get(mac_address=request.POST.get('interface'))
            if request.POST.get('network') is not None:
                network = Network.objects.get(name=request.POST.get('network'))
                ip_address = get_free_ip_from(network)
            if request.POST.get('ns') is not None and \
                    request.POST.get('domain') is not None:
                domain = Domain.objects.get(name=request.POST.get('domain'))
                ns = DomainEntry.objects.get(name=request.POST.get('ns'), domain=domain)
            if request.POST.get('ip-address') is not None:
                ip_address = request.POST.get('ip-address')
                network = get_network_from(ip_address)
            options = {
                'interface': interface,
                'network': network,
                'name': uri_host,
                'ip_address': ip_address,
                'dns_entry': ns
            }
            host = Host(**options)
            host.clean_fields()
            host.save()
            result = {
                'status': 'done',
                'host': uri_host
            }
        except IntegrityError as err:
            result = {
                'host': uri_host,
                'status': '{}'.format(err)
            }
        except ObjectDoesNotExist as err:
            result = {
                'host': uri_host,
                'status': '{}'.format(err)
            }
    elif request.method == 'DELETE':
        try:
            host = Host.objects.get(name=uri_host)
            host.delete()
            result = {
                'host': uri_host,
                'status': 'done'
            }
        except ObjectDoesNotExist as err:
            result = {
                'host': uri_host,
                'status': '{}'.format(err)
            }
    elif request.method == 'GET':
        try:
            host = Host.objects.get(name=uri_host)
            result = {
                'name': host.name,
            }
            if host.dns_entry is not None:
                result['dns_entry'] = host.dns_entry.name
            if host.interface is not None:
                result['interface'] = host.interface.mac_address
            if host.network is not None:
                result['network'] = {
                    'name': host.network.name
                }
            if host.ip_address is not None:
                result['network']['ip_address'] = host.ip_address
        except ObjectDoesNotExist as err:
            result = {
                'host': uri_host,
                'status': '{}'.format(err)
            }
    return JsonResponse(result)
