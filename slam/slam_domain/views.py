from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required
from slam_domain.models import Domain


@login_required
def domains(request):
    result = []
    data = Domain.objects.all()
    for current_domain in data:
        result.append({
            'name': current_domain.name,
            'description': current_domain.description,
            'master': current_domain.dns_master,
            'contact': current_domain.contact
        })
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)
    return render(request, 'domains/index.html', dict())


@login_required
def domain(request, name):
    rest_api = False
    result = {}
    if request.headers['Accept'] == 'application/json' or \
            request.GET.get('format') == 'json':
        rest_api = True
    if request.method == 'POST':
        description = request.POST.get('description')
        master = request.POST.get('master')
        contact = request.POST.get('contact')
        options = dict()
        options['name'] = name
        if description is not None:
            options['description'] = description
        if master is not None:
            options['dns_master'] = master
        if contact is not None:
            options['contact'] = contact
        Domain.objects.create(**options)
        result = {
            'domain': name,
            'status': 'done'
        }
    elif request.method == 'PUT':
        raw_data = request.body
        data = QueryDict(raw_data)
        description = data.get('description')
        master = data.get('master')
        contact = data.get('contact')
        item = Domain.objects.get(name=name)
        if description is not None:
            item.description = description
        if master is not None:
            item.master = master
        if contact is not None:
            item.contact = contact
        item.save()
        result = {
            'domain': name,
            'status': 'done'
        }
    if rest_api:
        return JsonResponse(result)
    else:
        # TODO: Create a html view for the output
        return JsonResponse(result)


@login_required
def dns_entry(request, name, ns_entry):
    print('Add DNS entry {} in {}'.format(ns_entry, name))
    rest_api = False
    result = {}
    if request.headers['Accept'] == 'application/json':
        rest_api = True
    if request.method == 'GET':
        result = {
            'domain': 'ijclab.in2p3.fr',
            'entry': 'www',
            'type': 'A'
        }
    if request.method == 'POST':
        result = {
            'domain': name,
            'entry': ns_entry,
            'status': 'done'
        }
    if rest_api:
        return JsonResponse(result)
    else:
        return JsonResponse(result)
