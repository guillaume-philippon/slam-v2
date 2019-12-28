from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def networks(request):
    result = [{
        'name': 'grid-lal',
        'description': 'Network for grid',
        'ip': '134.158.72.0',
        'gateway': '134.158.72.1',
        'prefix': '23',
        'vlan': 1901,
        'dhcp': '134.158.72.10'
    }]
    return JsonResponse(result, safe=False)


@login_required
def network(request, name):
    result = {
        'name': 'grid-lal',
        'description': 'Network for grid',
        'ip': '134.158.72.0',
        'gateway': '134.158.72.1',
        'prefix': '23',
        'vlan': 1901,
        'dhcp': '134.158.72.10'
    }
    return JsonResponse(result, safe=False)
