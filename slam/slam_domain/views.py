"""
This module provide different view to manage domain. To avoid shadow name declaration, we use those
following nomenclature
 - *_view: a function that manage the web interface (per example domains_view manage web interface
 of domains, ...)
 - domain: a specific domain (per example ijclab.in2p3.fr)
 - domains: a list of domain
 - entry: a name associated with a domain that represent a entry in DNS
 - entries: a list of entry
 - rest_api: a boolean which say if REST API is used. If not, HTML rendering will be used
 - options: a generic structure that represent arguments we send/receive to/from function
 - result: a temporary structure that represent the output of the view
 - result_*: a temporary structure that represent a part of the output (per example result_entries)
 - uri_*: input retrieve from URI structure itself
"""
from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required
from slam_domain.models import Domain, DomainEntry


@login_required
def domains_view(request):
    """
    This function manage interaction between user and SLAM for all domains management. URI is
    represented by https://slam.example.com/domains

    :param request: full HTTP request from user
    """
    result = []
    domains = Domain.objects.all()
    for domain in domains:
        result.append({
            'name': domain.name,
            'description': domain.description,
            'master': domain.dns_master,
            'contact': domain.contact
        })
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)
    return render(request, 'domains/index.html', dict())


@login_required
def domain_view(request, uri_domain):
    """
    This function manage interaction between user and SLAM for a specific domain management. URI
    is represented by https://slam.example.com/domains/example.com

    :param request: full HTTP request from user
    :param uri_domain: the name of domain from URI (per example example.com is our URI)
    """
    rest_api = False
    result = {}
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        rest_api = True
    if request.method == 'GET':
        domain = Domain.objects.get(name=uri_domain)
        entries = DomainEntry.objects.filter(domain=domain)
        result_entries = []
        for entry in entries:
            result_entries.append({
                'name': entry.name,
                'type': entry.type,
                'description': entry.description
            })
        result = {
            'domain': uri_domain,
            'description': domain.description,
            'contact': domain.contact,
            'master': domain.dns_master,
            'entries': result_entries
        }
    elif request.method == 'POST':
        description = request.POST.get('description')
        master = request.POST.get('master')
        contact = request.POST.get('contact')
        options = dict()
        options['name'] = uri_domain
        if description is not None:
            options['description'] = description
        if master is not None:
            options['dns_master'] = master
        if contact is not None:
            options['contact'] = contact
        Domain.objects.create(**options)
        result = {
            'domain': uri_domain,
            'status': 'done'
        }
    elif request.method == 'PUT':
        raw_data = request.body
        data = QueryDict(raw_data)
        description = data.get('description')
        master = data.get('master')
        contact = data.get('contact')
        item = Domain.objects.get(name=uri_domain)
        if description is not None:
            item.description = description
        if master is not None:
            item.master = master
        if contact is not None:
            item.contact = contact
        item.save()
        result = {
            'domain': uri_domain,
            'status': 'done'
        }
    if rest_api:
        return JsonResponse(result)
    else:
        # TODO: Create a html view for the output
        return JsonResponse(result)


@login_required
def entry_view(request, uri_domain, uri_entry):
    """
    This function manage interaction between user and SLAM for a specific domain management. URI
    is represented by https://slam.example.com/domains/example.com/www if we want to represent
    www.example.com

    :param request: full HTTP request from user
    :param uri_domain: the name of domain from URI (per example example.com in our URI)
    :param uri_entry: the entry name in a domain (per example www.example.com in our URI)
    """
    rest_api = False
    result = {}
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        rest_api = True
    if request.method == 'GET':
        domain = Domain.objects.get(name=uri_domain)
        entry = DomainEntry.objects.get(name=uri_entry, domain=domain)
        result = {
            'domain': uri_domain,
            'entry': uri_entry,
            'fqdn': "{}.{}".format(uri_entry, uri_domain),  # TODO: Is it necessary ?
            'type': entry.type
        }
    if request.method == 'POST':
        domain = Domain.objects.get(name=uri_domain)
        options = {
            'name': uri_entry,
            'domain': domain,
        }
        if request.POST.get('type') is not None:
            options['type'] = request.POST.get('type')
        if request.POST.get('description') is not None:
            options['description'] = request.POST.get('description')
        DomainEntry.objects.create(**options)
        result = {
            'domain': uri_domain,
            'entry': uri_entry,
            'status': 'done'
        }
    if rest_api:
        return JsonResponse(result)
    else:
        return JsonResponse(result)
