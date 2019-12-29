"""
This module provide different view to manage domain. To avoid shadow name declaration, we use those
following nomenclature
 - *_view: a function that manage the web interface (per example domains_view manage web interface
 of domains, ...)
 - domain: a specific domain (per example example.com)
 - domains: a list of domain
 - entry: a name associated with a domain that represent a entry in DNS
 - entries: a list of entry

 - rest_api: a boolean which say if REST API is used. If not, HTML rendering will be used
 - options: a generic structure that represent arguments we send/receive to/from function
 - result: a temporary structure that represent the output of the view
 - result_*: a temporary structure that represent a part of the output (per example result_entries)
 - uri_*: input retrieve from URI structure itself

 As django models are generic classes, pylint can't check if member of model Class exists, we must
 disable pylint E1101 (no-member) test from this file
"""
# pylint: disable=E1101
from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError

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
            'description': domain.description
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
    if request.method == 'GET':
        # If we just want to retrieve (GET) information for the domain. We're looking for
        # domain and all entries associated to it.
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
            'dns_master': domain.dns_master,
            'entries': result_entries
        }
    elif request.method == 'POST':
        # If we want to create (POST) a new domain. We retrieve optional information and create
        # a new object
        options = {
            'name': uri_domain,
        }
        for args in request.POST:
            options[args] = request.POST.get(args)
        try:
            Domain.objects.create(**options)
            result = {
                'domain': uri_domain,
                'status': 'done'
            }
        except IntegrityError as err:
            result = {
                'domain': uri_domain,
                'status': '{}'.format(err)
            }
    elif request.method == 'PUT':
        # If we want to update (PUT) a existing domain. We retrieve all mutable value and change it.
        raw_data = request.body
        data = QueryDict(raw_data)
        domain = Domain.objects.get(name=uri_domain)
        for args in data:
            setattr(domain, args, data.get(args))
        domain.save()
        result = {
            'domain': uri_domain,
            'status': 'done'
        }
    elif request.method == 'DELETE':
        # If we want to delete (DELETE) a existing domain, we just do it.
        domain = Domain.objects.get(name=uri_domain)
        domain.delete()
        result = {
            'domain': uri_domain,
            'status': 'done'
        }
    else:
        # We just support GET / POST / PUT / DELETE HTTP method. If anything else arrived, we
        # just drop it
        result = {
            'domain': uri_domain,
            'status': '{} method is not supported'.format(request.method)
        }
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
    if request.method == 'GET':
        # If we want a list of entries, we need to retrieve domain and list all entries associated
        # with it.
        domain = Domain.objects.get(name=uri_domain)
        entry = DomainEntry.objects.get(name=uri_entry, domain=domain)
        result = {
            'domain': uri_domain,
            'entry': uri_entry,
            'fqdn': "{}.{}".format(uri_entry, uri_domain),  # TODO: Is it necessary ?
            'type': entry.type
        }
    elif request.method == 'POST':
        # If we want to create a new entry, we need to retrieve the domain and add the entry on
        # this domain.
        domain = Domain.objects.get(name=uri_domain)
        options = {
            'name': uri_entry,
            'domain': domain,
        }
        # for args in request.POST:
        #     options[args] = request.POST.get(args)
        if request.POST.get('type') is not None:
            options['type'] = request.POST.get('type')
        if request.POST.get('description') is not None:
            options['description'] = request.POST.get('description')
        try:
            DomainEntry.objects.create(**options)
            result = {
                'domain': uri_domain,
                'entry': uri_entry,
                'status': 'done'
            }
        except IntegrityError as err:
            result = {
                'domain': uri_domain,
                'entry': uri_entry,
                'status': '{}'.format(err),
            }
    elif request.method == 'DELETE':
        # If we want to remove a specific entry, we must retrieve the entry associated with the
        # right domain and delete it.
        domain = Domain.objects.get(name=uri_domain)
        entry = DomainEntry.objects.get(name=uri_entry, domain=domain)
        entry.delete()
        result = {
            'status': 'done'
        }
    return JsonResponse(result)
