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
    result = Domain.search()
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
        result = Domain.get(uri_domain)
    elif request.method == 'POST':
        # If we want to create (POST) a new domain. We retrieve optional information and create
        # a new object.
        options = dict()
        for args in request.POST:
            # We don't care about the saintly of options as Domain.create take care of it.
            options[args] = request.POST.get(args)
        result = Domain.create(name=uri_domain, args=options)
    elif request.method == 'PUT':
        # If we want to update (PUT) a existing domain. We retrieve all mutable value and change it.
        raw_data = request.body
        data = QueryDict(raw_data)
        options = dict()
        for args in data:
            # We don't care about the saintly of options as Domain.update take care of it.
            options[args] = data.get(args)
        result = Domain.update(uri_domain, args=options)
    elif request.method == 'DELETE':
        # If we want to delete (DELETE) a existing domain, we just do it.
        result = Domain.remove(uri_domain)
    else:
        # We just support GET / POST / PUT / DELETE HTTP method. If anything else arrived, we
        # just drop it
        result = {
            'domain': uri_domain,
            'status': 'failed',
            'message': '{} method is not supported'.format(request.method)
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
        result = DomainEntry.get(name=uri_entry, domain=uri_domain)
    elif request.method == 'POST':
        # If we want to create a new entry, we need to retrieve the domain and add the entry on
        # this domain.
        options = {
            'name': uri_entry,
            'domain': uri_domain,
        }
        if request.POST.get('ns_type') is not None:
            options['ns_type'] = request.POST.get('ns_type')
        if request.POST.get('sub_entry_name') is not None:
            options['sub_entry'] = {
                'name': request.POST.get('sub_entry_name'),
                'domain': request.POST.get('sub_entry_domain'),
                'type': request.POST.get('sub_entry_type')
            }
        print(options)
        result = DomainEntry.create(**options)
    elif request.method == 'DELETE':
        # If we want to remove a specific entry, we must retrieve the entry associated with the
        # right domain and delete it.
        raw_data = request.body
        data = QueryDict(raw_data)
        if data.get('type') is not None:
            result = DomainEntry.remove(uri_entry, uri_domain, ns_type=data.get('type'))
        else:
            result = DomainEntry.remove(uri_entry, uri_domain)
    elif request.method == 'PUT':
        raw_data = request.body
        data = QueryDict(raw_data)
        options = {
            'name': uri_entry,
            'domain': uri_domain,
        }
        if data.get('type') is not None:
            options['ns_type'] = data.get('type')
        if data.get('sub_entry_name') is not None:
            options['sub_entry'] = {
                'name': data.get('sub_entry_name'),
                'domain': data.get('sub_entry_domain')
            }
        print(options)
        result = DomainEntry.update(**options)
    else:
        # We just support GET / POST / PUT / DELETE HTTP method. If anything else arrived, we
        # just drop it.
        result = {
            'entry': '{}.{}'.format(uri_entry, uri_domain),
            'status': 'failed',
            'message': '{} method is not supported'.format(request.method)
        }
    return JsonResponse(result)
